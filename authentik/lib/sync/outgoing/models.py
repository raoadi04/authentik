from typing import Any, Self

import pglock
from django.db import connection
from django.db.models import Model, QuerySet, TextChoices

from authentik.core.models import Group, User
from authentik.lib.sync.outgoing import LOCK_ACQUIRE_TIMEOUT
from authentik.lib.sync.outgoing.base import BaseOutgoingSyncClient


class OutgoingSyncDeleteAction(TextChoices):
    """Action taken when a user/group is deleted in authentik. Suspend is not available for groups,
    and will be treated as `do_nothing`"""

    DO_NOTHING = "do_nothing"
    DELETE = "delete"
    SUSPEND = "suspend"


class OutgoingSyncProvider(Model):

    class Meta:
        abstract = True

    def client_for_model[
        T: User | Group
    ](self, model: type[T]) -> BaseOutgoingSyncClient[T, Any, Any, Self]:
        raise NotImplementedError

    def get_object_qs[T: User | Group](self, type: type[T]) -> QuerySet[T]:
        raise NotImplementedError

    @property
    def sync_lock(self) -> pglock.advisory:
        """Postgres lock for syncing SCIM to prevent multiple parallel syncs happening"""
        return pglock.advisory(
            lock_id=f"goauthentik.io/providers/outgoing-sync/{connection.schema_name}/{str(self.pk)}",
            timeout=LOCK_ACQUIRE_TIMEOUT,
            side_effect=pglock.Raise,
        )
