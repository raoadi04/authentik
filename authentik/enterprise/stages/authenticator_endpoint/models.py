"""Endpoint stage"""

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import BaseSerializer, Serializer

from authentik.core.types import UserSettingSerializer
from authentik.flows.models import ConfigurableStage, FriendlyNamedStage, Stage
from authentik.flows.stage import StageView
from authentik.lib.models import SerializerModel
from authentik.stages.authenticator.models import Device


class AuthenticatorEndpointStage(ConfigurableStage, FriendlyNamedStage, Stage):
    """Setup Endpoint authenticator devices"""

    @property
    def serializer(self) -> type[BaseSerializer]:
        from authentik.enterprise.stages.authenticator_endpoint.api import (
            AuthenticatorEndpointStageSerializer,
        )

        return AuthenticatorEndpointStageSerializer

    @property
    def view(self) -> type[StageView]:
        from authentik.enterprise.stages.authenticator_endpoint.stage import (
            AuthenticatorEndpointStageView,
        )

        return AuthenticatorEndpointStageView

    @property
    def component(self) -> str:
        return "ak-stage-authenticator-endpoint-form"

    def ui_user_settings(self) -> UserSettingSerializer | None:
        return UserSettingSerializer(
            data={
                "title": self.friendly_name or str(self._meta.verbose_name),
                "component": "ak-user-settings-authenticator-endpoint",
            }
        )

    def __str__(self) -> str:
        return f"Endpoint Authenticator Setup Stage {self.name}"

    class Meta:
        verbose_name = _("Endpoint Authenticator Setup Stage")
        verbose_name_plural = _("Endpoint Authenticator Setup Stages")


class EndpointDevice(SerializerModel, Device):
    """Endpoint Device for a single user"""

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    host_identifier = models.TextField(
        unique=True,
        help_text="A unique identifier for the endpoint device, usually the device serial number",
    )

    hostname = models.TextField()

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    @property
    def serializer(self) -> Serializer:
        from authentik.enterprise.stages.authenticator_endpoint.api import EndpointDeviceSerializer

        return EndpointDeviceSerializer

    def __str__(self):
        return str(self.name) or str(self.user_id)

    class Meta:
        verbose_name = _("Endpoint Device")
        verbose_name_plural = _("Endpoint Devices")


class EndpointDeviceConnection(models.Model):

    device = models.ForeignKey(EndpointDevice, on_delete=models.CASCADE)
    stage = models.ForeignKey(AuthenticatorEndpointStage, on_delete=models.CASCADE)

    attributes = models.JSONField()

    def __str__(self) -> str:
        return f"Endpoint device connection {self.device_id} to {self.stage_id}"
