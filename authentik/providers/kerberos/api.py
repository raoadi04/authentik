"""KerberosProvider API Views"""
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.fields import CharField, ListField, ReadOnlyField, SerializerMethodField
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from authentik.core.api.providers import ProviderSerializer
from authentik.core.api.used_by import UsedByMixin
from authentik.core.api.utils import MetaNameSerializer
from authentik.providers.kerberos.lib.protocol import PrincipalName
from authentik.providers.kerberos.models import KerberosProvider, KerberosRealm


class KerberosRealmSerializer(ModelSerializer, MetaNameSerializer):
    """KerberosRealm Serializer"""

    provider_set = ListField(
        child=CharField(),
        read_only=True,
        source="kerberosprovider_set.all",
    )

    class Meta:
        model = KerberosRealm
        fields = [
            "pk",
            "name",
            "authentication_flow",
            "maximum_skew",
            "maximum_ticket_lifetime",
            "maximum_ticket_renew_lifetime",
            "allowed_enctypes",
            "allow_postdateable",
            "allow_renewable",
            "allow_proxiable",
            "allow_forwardable",
            "requires_preauth",
            "secret",
            "provider_set",
            "meta_model_name",
        ]


class KerberosRealmViewSet(UsedByMixin, ModelViewSet):
    """KerberosRealm Viewset"""

    queryset = KerberosRealm.objects.all()
    serializer_class = KerberosRealmSerializer
    ordering = ["name"]
    search_fields = ["name"]
    filterset_fields = {
        "name": ["iexact"],
        "authentication_flow__slug": ["iexact"],
    }


class KerberosProviderSerializer(ProviderSerializer):
    """KerberosProvider Serializer"""

    realm_name = ReadOnlyField(source="realm.name")
    url_download_keytab = SerializerMethodField()

    class Meta:
        model = KerberosProvider
        fields = ProviderSerializer.Meta.fields + [
            "realm",
            "realm_name",
            "service_principal_name",
            "set_ok_as_delegate",
            "maximum_ticket_lifetime",
            "maximum_ticket_renew_lifetime",
            "allowed_enctypes",
            "allow_postdateable",
            "allow_renewable",
            "allow_proxiable",
            "allow_forwardable",
            "requires_preauth",
            "secret",
            "url_download_keytab",
            "full_spn",
        ]
        extra_kwargs = {}

    def get_url_download_keytab(self, instance: KerberosProvider) -> str:
        """Get URL where to download provider's keytab"""
        if "request" not in self._context:
            return ""
        request: HttpRequest = self._context["request"]._request
        return request.build_absolute_uri(
            reverse("authentik_api:kerberosprovider-keytab", kwargs={"pk": instance.pk})
        )


class KerberosProviderViewSet(UsedByMixin, ModelViewSet):
    """KerberosProvider Viewset"""

    queryset = KerberosProvider.objects.all()
    serializer_class = KerberosProviderSerializer
    ordering = ["name"]
    search_fields = ["name", "realm__name"]
    filterset_fields = {
        "application": ["isnull"],
        "name": ["iexact"],
        "authorization_flow__slug": ["iexact"],
        "realm__name": ["iexact"],
    }

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Service keytab"),
        }
    )
    @action(detail=True, methods=["GET"])
    def keytab(self, request: Request, pk: str) -> HttpResponse:
        """Retrieve the provider keytab"""
        provider: KerberosProvider = self.get_object()
        keytab = provider.kerberoskeys.keytab(
            PrincipalName.from_spn(provider.service_principal_name), provider.realm
        )
        return HttpResponse(
            keytab.to_bytes(),
            content_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=krb5.keytab",
            },
        )
