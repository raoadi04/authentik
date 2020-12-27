"""SAML ServiceProvider Metadata Parser and dataclass"""
from base64 import b64decode
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote_plus
from xml.etree.ElementTree import Element

import xmlsec
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from defusedxml import ElementTree
from lxml import etree  # nosec
from structlog import get_logger

from authentik.crypto.models import CertificateKeyPair
from authentik.providers.saml.exceptions import CannotHandleAssertion
from authentik.providers.saml.models import SAMLBindings, SAMLProvider
from authentik.providers.saml.utils.encoding import (
    PEM_FOOTER,
    PEM_HEADER,
    decode_base64_and_inflate,
)
from authentik.sources.saml.processors.constants import (
    DSA_SHA1,
    NS_MAP,
    NS_SAML_METADATA,
    NS_SAML_PROTOCOL,
    RSA_SHA1,
    RSA_SHA256,
    RSA_SHA384,
    RSA_SHA512,
    SAML_BINDING_POST,
    SAML_BINDING_REDIRECT,
    SAML_NAME_ID_FORMAT_EMAIL,
)

LOGGER = get_logger()


def format_pem_certificate(unformatted_cert: str) -> str:
    """Format single, inline certificate into PEM Format"""
    chunks, chunk_size = len(unformatted_cert), 64
    lines = [unformatted_cert[i : i + chunk_size] for i in range(0, chunks, chunk_size)]
    lines.insert(0, PEM_HEADER)
    lines.append(PEM_FOOTER)
    return "\n".join(lines)


@dataclass
class ServiceProviderMetadata:
    """SP Metadata Dataclass"""

    entity_id: str

    acs_binding: SAMLBindings
    acs_location: str

    auth_n_request_signed: bool
    assertion_signed: bool

    signing_keypair: Optional[CertificateKeyPair] = None

    def to_provider(self, name: str) -> SAMLProvider:
        """Create a SAMLProvider instance from the details. `name` is required,
        as depending on the metadata CertificateKeypairs might have to be created."""
        provider = SAMLProvider(name=name)
        provider.issuer = self.entity_id
        provider.sp_binding = self.acs_binding
        provider.acs_url = self.acs_location
        if self.signing_keypair:
            provider.signing_kp = self.signing_keypair
        return provider


class ServiceProviderMetadataParser:
    """Service-Provider Metadata Parser"""

    def get_signing_cert(self, root: etree.Element) -> Optional[CertificateKeyPair]:
        """Extract X509Certificate from metadata, when given."""
        signing_certs = root.xpath(
            '//md:SPSSODescriptor/md:KeyDescriptor[@use="signing"]//ds:X509Certificate/text()',
            namespaces=NS_MAP,
        )
        if len(signing_certs) < 1:
            return None
        raw_cert = format_pem_certificate(signing_certs[0])
        # sanity check, make sure the certificate is valid.
        load_pem_x509_certificate(raw_cert.encode("utf-8"), default_backend())
        return CertificateKeyPair(
            certificate_data=raw_cert,
        )

    def check_signature(self, root: Element, keypair: CertificateKeyPair):
        """If Metadata is signed, check validity of signature"""
        xmlsec.tree.add_ids(root, ["ID"])
        signature_nodes = root.xpath(
            "/md:EntityDescriptor/ds:Signature", namespaces=NS_MAP
        )
        if len(signature_nodes) != 1:
            # No Signature
            return

        signature_node = signature_nodes[0]

        if signature_node is not None:
            try:
                ctx = xmlsec.SignatureContext()
                key = xmlsec.Key.from_memory(
                    keypair.certificate_data,
                    xmlsec.constants.KeyDataFormatCertPem,
                    None,
                )
                ctx.key = key
                ctx.verify(signature_node)
            except xmlsec.VerificationError as exc:
                raise ValueError("Failed to verify Metadata signature") from exc

    def parse(self, raw_xml: str) -> ServiceProviderMetadata:
        """Parse raw XML to ServiceProviderMetadata"""
        root = etree.fromstring(raw_xml)  # nosec

        entity_id = root.attrib["entityID"]
        sp_sso_descriptors = root.findall(f"{{{NS_SAML_METADATA}}}SPSSODescriptor")
        if len(sp_sso_descriptors) < 1:
            raise ValueError("no SPSSODescriptor objects found.")
        # For now we'll only look at the first descriptor.
        # Even if multiple descriptors exist, we can only configure one
        descriptor = sp_sso_descriptors[0]
        auth_n_request_signed = descriptor.attrib["AuthnRequestsSigned"]
        assertion_signed = descriptor.attrib["WantAssertionsSigned"]

        acs_services = descriptor.findall(
            f"{{{NS_SAML_METADATA}}}AssertionConsumerService"
        )
        if len(acs_services) < 1:
            raise ValueError("No AssertionConsumerService found.")

        acs_service = acs_services[0]
        acs_binding = {
            SAML_BINDING_REDIRECT: SAMLBindings.REDIRECT,
            SAML_BINDING_POST: SAMLBindings.POST,
        }[acs_service.attrib["Binding"]]
        acs_location = acs_service.attrib["Location"]

        signing_keypair = self.get_signing_cert(root)
        self.check_signature(root, signing_keypair)

        return ServiceProviderMetadata(
            entity_id=entity_id,
            acs_binding=acs_binding,
            acs_location=acs_location,
            auth_n_request_signed=auth_n_request_signed,
            assertion_signed=assertion_signed,
            signing_keypair=signing_keypair,
        )
