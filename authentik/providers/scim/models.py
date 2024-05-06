"""SCIM Provider models"""

from uuid import uuid4

from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from redis.lock import Lock
from rest_framework.serializers import Serializer

from authentik.core.models import BackchannelProvider, Group, PropertyMapping, User, UserTypes
from authentik.providers.scim.clients import PAGE_TIMEOUT


class SCIMProvider(BackchannelProvider):
    """SCIM 2.0 provider to create users and groups in external applications"""

    exclude_users_service_account = models.BooleanField(default=False)

    filter_group = models.ForeignKey(
        "authentik_core.group", on_delete=models.SET_DEFAULT, default=None, null=True
    )

    url = models.TextField(help_text=_("Base URL to SCIM requests, usually ends in /v2"))
    token = models.TextField(help_text=_("Authentication token"))

    property_mappings_group = models.ManyToManyField(
        PropertyMapping,
        default=None,
        blank=True,
        help_text=_("Property mappings used for group creation/updating."),
    )

    @property
    def sync_lock(self) -> Lock:
        """Redis lock for syncing SCIM to prevent multiple parallel syncs happening"""
        return Lock(
            cache.client.get_client(),
            name=f"goauthentik.io/providers/scim/sync-{str(self.pk)}",
            timeout=(60 * 60 * PAGE_TIMEOUT) * 3,
        )

    def get_user_qs(self) -> QuerySet[User]:
        """Get queryset of all users with consistent ordering
        according to the provider's settings"""
        base = User.objects.all().exclude_anonymous()
        if self.exclude_users_service_account:
            base = base.exclude(type=UserTypes.SERVICE_ACCOUNT).exclude(
                type=UserTypes.INTERNAL_SERVICE_ACCOUNT
            )
        if self.filter_group:
            base = base.filter(ak_groups__in=[self.filter_group])
        return base.order_by("pk")

    def get_group_qs(self) -> QuerySet[Group]:
        """Get queryset of all groups with consistent ordering"""
        return Group.objects.all().order_by("pk")

    @property
    def component(self) -> str:
        return "ak-provider-scim-form"

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.providers.scim.api.providers import SCIMProviderSerializer

        return SCIMProviderSerializer

    def __str__(self):
        return f"SCIM Provider {self.name}"

    class Meta:
        verbose_name = _("SCIM Provider")
        verbose_name_plural = _("SCIM Providers")


class SCIMMapping(PropertyMapping):
    """Map authentik data to outgoing SCIM requests"""

    @property
    def component(self) -> str:
        return "ak-property-mapping-scim-form"

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.providers.scim.api.property_mapping import SCIMMappingSerializer

        return SCIMMappingSerializer

    def __str__(self):
        return f"SCIM Mapping {self.name}"

    class Meta:
        verbose_name = _("SCIM Mapping")
        verbose_name_plural = _("SCIM Mappings")


class SCIMUser(models.Model):
    """Mapping of a user and provider to a SCIM user ID"""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    scim_id = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(SCIMProvider, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("scim_id", "user", "provider"),)

    def __str__(self) -> str:
        return f"SCIM User {self.user_id} to {self.provider_id}"


class SCIMGroup(models.Model):
    """Mapping of a group and provider to a SCIM user ID"""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    scim_id = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    provider = models.ForeignKey(SCIMProvider, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("scim_id", "group", "provider"),)

    def __str__(self) -> str:
        return f"SCIM Group {self.group_id} to {self.provider_id}"
