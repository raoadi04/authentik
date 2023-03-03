"""SCIM Provider tasks"""
from celery.result import allow_join_result
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import get_anonymous_user
from structlog.stdlib import get_logger

from authentik.core.models import Group, User
from authentik.events.monitored_tasks import MonitoredTask, TaskResult, TaskResultStatus
from authentik.providers.scim.clients import PAGE_SIZE
from authentik.providers.scim.clients.base import SCIMClient
from authentik.providers.scim.clients.exceptions import SCIMRequestException, StopSync
from authentik.providers.scim.clients.group import SCIMGroupClient
from authentik.providers.scim.clients.user import SCIMUserClient
from authentik.providers.scim.models import SCIMProvider
from authentik.root.celery import CELERY_APP

LOGGER = get_logger(__name__)


@CELERY_APP.task()
def scim_sync_all():
    """Run sync for all providers"""
    for provider in SCIMProvider.objects.all():
        scim_sync.delay(provider.pk)


@CELERY_APP.task(bind=True, base=MonitoredTask)
def scim_sync(self: MonitoredTask, provider_pk: int) -> None:
    """Run SCIM full sync for provider"""
    provider: SCIMProvider = SCIMProvider.objects.filter(pk=provider_pk).first()
    if not provider:
        return
    self.set_uid(slugify(provider.name))
    result = TaskResult(TaskResultStatus.SUCCESSFUL, [])
    result.messages.append(_("Starting full SCIM sync"))
    # TODO: Filtering
    LOGGER.debug("Starting SCIM sync")
    users_paginator = Paginator(
        User.objects.all().exclude(pk=get_anonymous_user().pk).order_by("pk"), PAGE_SIZE
    )
    groups_paginator = Paginator(Group.objects.all().order_by("pk"), PAGE_SIZE)
    with allow_join_result():
        try:
            for page in users_paginator.page_range:
                result.messages.append(_("Syncing page %(page)d of users" % {"page": page}))
                for msg in scim_sync_users.delay(page, provider_pk).get():
                    result.messages.append(msg)
            for page in groups_paginator.page_range:
                result.messages.append(_("Syncing page %(page)d of groups" % {"page": page}))
                for msg in scim_sync_group.delay(page, provider_pk).get():
                    result.messages.append(msg)
        except StopSync as exc:
            self.set_status(TaskResult(TaskResultStatus.ERROR).with_error(exc))
            return
    self.set_status(result)


@CELERY_APP.task()
def scim_sync_users(page: int, provider_pk: int, **kwargs):
    """Sync single or multiple users to SCIM"""
    provider: SCIMProvider = SCIMProvider.objects.filter(pk=provider_pk).first()
    if not provider:
        return []
    client = SCIMClient(provider)
    user_client = SCIMUserClient(client)
    paginator = Paginator(
        User.objects.all().filter(**kwargs).exclude(pk=get_anonymous_user().pk).order_by("pk"),
        PAGE_SIZE,
    )
    LOGGER.debug("starting user sync for page", page=page)
    messages = []
    for user in paginator.page(page).object_list:
        try:
            user_client.write(user)
        except SCIMRequestException as exc:
            LOGGER.warning("failed to sync user", exc=exc, user=user)
            messages.append(
                _(
                    "Failed to sync user due to remote error %(name)s: %(error)s"
                    % {
                        "name": user.username,
                        "error": str(exc),
                    }
                )
            )
    return messages


@CELERY_APP.task()
def scim_sync_group(page: int, provider_pk: int, **kwargs):
    """Sync single or multiple groups to SCIM"""
    provider: SCIMProvider = SCIMProvider.objects.filter(pk=provider_pk).first()
    if not provider:
        return []
    client = SCIMClient(provider)
    group_client = SCIMGroupClient(client)
    paginator = Paginator(Group.objects.all().filter(**kwargs).order_by("pk"), PAGE_SIZE)
    LOGGER.debug("starting group sync for page", page=page)
    messages = []
    for group in paginator.page(page).object_list:
        try:
            group_client.write(group)
        except SCIMRequestException as exc:
            LOGGER.warning("failed to sync group", exc=exc, group=group)
            messages.append(
                _(
                    "Failed to sync group due to remote error %(name)s: %(error)s"
                    % {
                        "name": group.name,
                        "error": str(exc),
                    }
                )
            )
    return messages
