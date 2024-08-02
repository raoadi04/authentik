"""authentik policy signals"""

from django.core.cache import cache
from django.db import connection
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from structlog.stdlib import get_logger

from authentik.core.api.applications import user_app_cache_key
from authentik.core.models import Group, User
from authentik.core.tasks import purge_password_history_table
from authentik.policies.apps import GAUGE_POLICIES_CACHED
from authentik.policies.models import Policy, PolicyBinding, PolicyBindingModel
from authentik.policies.types import CACHE_PREFIX
from authentik.root.monitoring import monitoring_set

LOGGER = get_logger()


@receiver(monitoring_set)
def monitoring_set_policies(sender, **kwargs):
    """set policy gauges"""
    GAUGE_POLICIES_CACHED.labels(tenant=connection.schema_name).set(
        len(cache.keys(f"{CACHE_PREFIX}*") or [])
    )


@receiver(post_save, sender=Policy)
@receiver(post_save, sender=PolicyBinding)
@receiver(post_save, sender=PolicyBindingModel)
@receiver(post_save, sender=Group)
@receiver(post_save, sender=User)
def invalidate_policy_cache(sender, instance, **_):
    """Invalidate Policy cache when policy is updated"""
    if sender == Policy:
        total = 0
        for binding in PolicyBinding.objects.filter(policy=instance):
            prefix = f"{CACHE_PREFIX}{binding.policy_binding_uuid.hex}_{binding.policy.pk.hex}*"
            keys = cache.keys(prefix)
            total += len(keys)
            cache.delete_many(keys)
        LOGGER.debug("Invalidating policy cache", policy=instance, keys=total)
    # Also delete user application cache
    keys = cache.keys(user_app_cache_key("*")) or []
    cache.delete_many(keys)


@receiver(post_delete, sender=PolicyBinding)
def purge_password_history(sender, instance, **_):
    from authentik.policies.unique_password.models import UniquePasswordPolicy

    if not isinstance(instance.policy, UniquePasswordPolicy):
        return

    unique_password_policies = UniquePasswordPolicy.objects.all()

    policy_binding_qs = PolicyBinding.objects.filter(policy__in=unique_password_policies).filter(
        enabled=True
    )

    if policy_binding_qs.count() > 1:
        # No-op; A UniquePasswordPolicy binding other than the one being deleted still exists
        return
    purge_password_history_table.delay()
