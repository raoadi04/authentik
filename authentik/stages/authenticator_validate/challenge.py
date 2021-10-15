"""Validation stage challenge checking"""
from django.http import HttpRequest
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_otp import match_token
from django_otp.models import Device
from rest_framework.fields import CharField, JSONField
from rest_framework.serializers import ValidationError
from structlog.stdlib import get_logger
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers.exceptions import InvalidAuthenticationResponse
from webauthn.helpers.structs import AuthenticationCredential, PublicKeyCredentialDescriptor

from authentik.core.api.utils import PassiveSerializer
from authentik.core.models import User
from authentik.lib.utils.http import get_client_ip
from authentik.stages.authenticator_duo.models import AuthenticatorDuoStage, DuoDevice
from authentik.stages.authenticator_sms.models import SMSDevice
from authentik.stages.authenticator_webauthn.models import WebAuthnDevice
from authentik.stages.authenticator_webauthn.utils import get_origin, get_rp_id

LOGGER = get_logger()


class DeviceChallenge(PassiveSerializer):
    """Single device challenge"""

    device_class = CharField()
    device_uid = CharField()
    challenge = JSONField()


def get_challenge_for_device(request: HttpRequest, device: Device) -> dict:
    """Generate challenge for a single device"""
    if isinstance(device, WebAuthnDevice):
        return get_webauthn_challenge(request, device)
    # Code-based challenges have no hints
    return {}


def get_webauthn_challenge(request: HttpRequest, device: WebAuthnDevice) -> dict:
    """Send the client a challenge that we'll check later"""
    request.session.pop("challenge", None)

    allowed_credentials = []

    # We want all the user's WebAuthn devices and merge their challenges
    for user_device in WebAuthnDevice.objects.filter(user=device.user).order_by("name"):
        user_device: WebAuthnDevice
        allowed_credentials.append(PublicKeyCredentialDescriptor(id=user_device.credential_id))

    authentication_options = generate_authentication_options(
        rp_id=get_rp_id(request),
        allow_credentials=allowed_credentials,
    )

    request.session["challenge"] = authentication_options.challenge

    return authentication_options.dict()


def select_challenge(request: HttpRequest, device: Device):
    """Callback when the user selected a challenge in the frontend."""
    if isinstance(device, SMSDevice):
        select_challenge_sms(request, device)


def select_challenge_sms(request: HttpRequest, device: SMSDevice):
    """Send SMS"""
    device.generate_token()
    device.stage.send(device.token, device)


def validate_challenge_code(code: str, request: HttpRequest, user: User) -> str:
    """Validate code-based challenges. We test against every device, on purpose, as
    the user mustn't choose between totp and static devices."""
    device = match_token(user, code)
    if not device:
        raise ValidationError(_("Invalid Token"))
    return code


def validate_challenge_webauthn(data: dict, request: HttpRequest, user: User) -> dict:
    """Validate WebAuthn Challenge"""
    challenge = request.session.get("challenge")
    credential_id = data.get("id")

    device = WebAuthnDevice.objects.filter(credential_id=credential_id).first()
    if not device:
        raise ValidationError("Device does not exist.")

    try:
        authentication_verification = verify_authentication_response(
            credential=AuthenticationCredential.parse_obj(data),
            expected_challenge=challenge,
            expected_rp_id=get_rp_id(request),
            expected_origin=get_origin(request),
            credential_public_key=device.public_key,
            credential_current_sign_count=device.sign_count,
            require_user_verification=False,
        )

    except (InvalidAuthenticationResponse) as exc:
        raise ValidationError("Assertion failed") from exc

    device.set_sign_count(authentication_verification.new_sign_count)
    return data


def validate_challenge_duo(device_pk: int, request: HttpRequest, user: User) -> int:
    """Duo authentication"""
    device = get_object_or_404(DuoDevice, pk=device_pk)
    if device.user != user:
        LOGGER.warning("device mismatch")
        raise Http404
    stage: AuthenticatorDuoStage = device.stage
    response = stage.client.auth(
        "auto",
        user_id=device.duo_user_id,
        ipaddr=get_client_ip(request),
        type="authentik Login request",
        display_username=user.username,
        device="auto",
    )
    # {'result': 'allow', 'status': 'allow', 'status_msg': 'Success. Logging you in...'}
    if response["result"] == "deny":
        raise ValidationError("Duo denied access")
    return device_pk
