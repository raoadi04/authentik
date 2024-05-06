"""Google workspace sync provider"""

from typing import Any, Self
from uuid import uuid4

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from google.oauth2.service_account import Credentials
from rest_framework.serializers import Serializer

from authentik.core.models import (
    BackchannelProvider,
    Group,
    PropertyMapping,
    User,
    UserTypes,
)
from authentik.lib.sync.outgoing.base import BaseOutgoingSyncClient
from authentik.lib.sync.outgoing.models import OutgoingSyncProvider


def default_scopes() -> list[str]:
    return [
        "https://www.googleapis.com/auth/admin.directory.user",
        "https://www.googleapis.com/auth/admin.directory.group",
        "https://www.googleapis.com/auth/admin.directory.group.member",
        "https://www.googleapis.com/auth/admin.directory.domain.readonly",
    ]


class GoogleWorkspaceProvider(OutgoingSyncProvider, BackchannelProvider):
    """Sync users from authentik into Google Workspace."""

    delegated_subject = models.EmailField()
    credentials = models.JSONField()
    scopes = models.TextField(default=",".join(default_scopes()))

    exclude_users_service_account = models.BooleanField(default=False)

    filter_group = models.ForeignKey(
        "authentik_core.group", on_delete=models.SET_DEFAULT, default=None, null=True
    )

    property_mappings_group = models.ManyToManyField(
        PropertyMapping,
        default=None,
        blank=True,
        help_text=_("Property mappings used for group creation/updating."),
    )

    def client_for_model(
        self, model: type[User | Group]
    ) -> BaseOutgoingSyncClient[User | Group, Any, Any, Self]:
        if issubclass(model, User):
            from authentik.enterprise.providers.google_workspace.clients.users import (
                GoogleWorkspaceUserClient,
            )

            return GoogleWorkspaceUserClient(self)
        if issubclass(model, Group):
            from authentik.enterprise.providers.google_workspace.clients.groups import (
                GoogleWorkspaceGroupClient,
            )

            return GoogleWorkspaceGroupClient(self)
        raise ValueError(f"Invalid model {model}")

    def get_object_qs(self, type: type[User | Group]) -> QuerySet[User | Group]:
        if type == User:
            # Get queryset of all users with consistent ordering
            # according to the provider's settings
            base = User.objects.all().exclude_anonymous()
            if self.exclude_users_service_account:
                base = base.exclude(type=UserTypes.SERVICE_ACCOUNT).exclude(
                    type=UserTypes.INTERNAL_SERVICE_ACCOUNT
                )
            if self.filter_group:
                base = base.filter(ak_groups__in=[self.filter_group])
            return base.order_by("pk")
        if type == Group:
            # Get queryset of all groups with consistent ordering
            return Group.objects.all().order_by("pk")
        raise ValueError(f"Invalid type {type}")

    def google_credentials(self):
        return Credentials.from_service_account_info(
            self.credentials, scopes=self.scopes.split(",")
        ).with_subject(self.delegated_subject)

    @property
    def component(self) -> str:
        return "ak-provider-google-workspace-form"

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.enterprise.providers.google_workspace.api.providers import (
            GoogleProviderSerializer,
        )

        return GoogleProviderSerializer

    def __str__(self):
        return f"Google Workspace Provider {self.name}"

    class Meta:
        verbose_name = _("Google Workspace Provider")
        verbose_name_plural = _("Google Workspace Providers")


class GoogleWorkspaceProviderMapping(PropertyMapping):
    """Map authentik data to outgoing Google requests"""

    @property
    def component(self) -> str:
        return "ak-property-mapping-google-workspace-form"

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.enterprise.providers.google_workspace.api.property_mappings import (
            GoogleProviderMappingSerializer,
        )

        return GoogleProviderMappingSerializer

    def __str__(self):
        return f"Google Workspace Provider Mapping {self.name}"

    class Meta:
        verbose_name = _("Google Workspace Provider Mapping")
        verbose_name_plural = _("Google Workspace Provider Mappings")


class GoogleWorkspaceProviderUser(models.Model):
    """Mapping of a user and provider to a Google user ID"""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    google_id = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(GoogleWorkspaceProvider, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("google_id", "user", "provider"),)

    def __str__(self) -> str:
        return f"Google Workspace User {self.user_id} to {self.provider_id}"


class GoogleWorkspaceProviderGroup(models.Model):
    """Mapping of a group and provider to a Google group ID"""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    google_id = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    provider = models.ForeignKey(GoogleWorkspaceProvider, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("google_id", "group", "provider"),)

    def __str__(self) -> str:
        return f"Google Workspace Group {self.group_id} to {self.provider_id}"
