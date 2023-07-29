"""authentik Kerberos views"""
from dataclasses import dataclass, field
from base64 import b64decode
from datetime import timedelta

from pyasn1.type import univ

from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import SuspiciousOperation
from structlog.stdlib import get_logger

from authentik.lib.kerberos import crypto, iana
from authentik.lib.kerberos.exceptions import KerberosError
from authentik.lib.kerberos.protocol import (
    AsRep,
    AsReq,
    KdcProxyMessage,
    KdcRep,
    KdcReq,
    KrbError,
    KeyUsageNumbers,
    PaData,
    TgsRep,
    TgsReq,
    Ticket,
    TransitedEncoding,
    EncryptedData,
    EncryptionKey,
    EncTicketPart,
    EncAsRepPart,
    PaDataEncTsEnc,
    PaDataEtypeInfo2,
    PaDataEtypeInfo2Entry,
    ApplicationTag,
    PrincipalNameType,
    PrincipalName,
    MethodData,
)
from authentik.lib.utils.time import timedelta_from_string
from authentik.providers.kerberos.models import KerberosProvider, KerberosRealm
from authentik.core.models import User

LOGGER = get_logger()


@dataclass
class Context:
    request: HttpRequest
    message: KdcReq
    realm: KerberosRealm | None = None
    user: User | None = None
    cname: PrincipalName | None = None
    sname: PrincipalName | None = None
    provider: KerberosProvider | None = None
    pa_data: MethodData = field(default_factory=MethodData)
    encrypted_part_key: bytes | None = None
    encrypted_part_kvno: int | None = None
    encrypted_part_enctype: crypto.EncryptionType | None = None
    client_authority: iana.PreAuthenticationType | None = None

    @property
    def preauth_satisfied(self) -> bool:
        return self.encrypted_part_key is not None

    def __post_init__(self):
        self.realm = KerberosRealm(name=self.message["req-body"]["realm"])
        self.sname = self.message["req-body"]["sname"]
        self.cname = self.message["req-body"]["cname"]


class PaHandler:
    PRE_AUTHENTICATION_TYPE: iana.PreAuthenticationType

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def pre_validate(self):
        pass

    def validate(self):
        pass

    def post_validate(self):
        pass


class PaEtypeInfo2(PaHandler):
    PRE_AUTHENTICATION_TYPE = iana.PreAuthenticationType.PA_ETYPE_INFO2

    def post_validate(self):
        if not self.ctx.user:
            return

        entries = PaDataEtypeInfo2()
        if self.ctx.encrypted_part_enctype:
            entry = PaDataEtypeInfo2Entry()
            entry["etype"] = self.ctx.encrypted_part_enctype.ENC_TYPE.value
            entry["salt"] = str(self.ctx.user.uuid).encode("utf-8")
            entry["s2kparams"] = self.ctx.encrypted_part_enctype.s2k_params()
            entries.append(entry)
        else:
            for enctype_value in map(int, self.ctx.user.krb5_keys.keys()):
                entry = PaDataEtypeInfo2Entry()
                entry["etype"] = enctype_value
                entry["salt"] = str(self.ctx.user.uuid).encode("utf-8")
                entry["s2kparams"] = crypto.get_enctype_from_value(enctype_value).s2k_params()
                entries.append(entry)

        padata = PaData()
        padata["padata-type"] = self.PRE_AUTHENTICATION_TYPE.value
        padata["padata-value"] = entries.to_bytes()
        self.ctx.pa_data.append(padata)


class PaEncTimestampHandler(PaHandler):
    PRE_AUTHENTICATION_TYPE = iana.PreAuthenticationType.PA_ENC_TIMESTAMP

    def _get_padata_timestamp(self):
        for padata in self.ctx.message.getComponentByName("padata", []):
            if padata["padata-type"] != iana.PreAuthenticationType.PA_ENC_TIMESTAMP.value:
                continue
            return padata
        return None

    def _check_padata_timestamp(self, paenctsenc: PaDataEncTsEnc) -> bool:
        patimestamp = paenctsenc["patimestamp"]
        pausec = paenctsenc.getComponentByName("pausec", 0)
        dt = patimestamp.asDateTime + timedelta(microseconds=int(pausec))
        target_entity = self.ctx.provider or self.ctx.realm
        skew = timedelta_from_string(target_entity.maximum_skew)
        return now() - skew < dt < now() + skew

    def validate(self):
        if self.ctx.preauth_satisfied:
            return

        padata = self._get_padata_timestamp()

        if padata is None:
            padata = PaData()
            padata["padata-type"] = self.PRE_AUTHENTICATION_TYPE.value
            padata["padata-value"] = bytes()
            self.ctx.pa_data.append(padata)
            return

        encdata = EncryptedData.from_bytes(padata["padata-value"])
        enctype_value = encdata["etype"]

        try:
            enctype = crypto.get_enctype_from_value(enctype_value)
        except IndexError as exc:
            raise KerberosError(code=KerberosError.Code.KDC_ERR_ETYPE_NOSUPP) from exc

        try:
            key = b64decode(self.ctx.user.krb5_keys[str(enctype_value)].encode())
        except IndexError as exc:
            raise KerberosError(code=KerberosError.Code.KDC_ERR_ETYPE_NOSUPP) from exc

        try:
            paenctsenc = PaDataEncTsEnc.from_bytes(
               enctype.decrypt_message(
                   key=key,
                   ciphertext=bytes(encdata["cipher"]),
                   usage=KeyUsageNumbers.AS_REQ_PA_ENC_TIMESTAMP.value,
               )
            )
        except ValueError as exc:
           raise KerberosError(code=KerberosError.Code.KDC_ERR_PREAUTH_FAILED) from exc

        if not self._check_padata_timestamp(paenctsenc):
           raise KerberosError(code=KerberosError.Code.KDC_ERR_PREAUTH_FAILED)

        self.ctx.encrypted_part_key = key
        self.ctx.encrypted_part_kvno = self.ctx.user.krb5_kvno
        self.ctx.encrypted_part_enctype = enctype
        self.ctx.client_authority = self.PRE_AUTHENTICATION_TYPE


class MessageHandler:
    PA_HANDLERS: list[PaHandler]

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.pa_handlers = [handler(ctx) for handler in self.PA_HANDLERS]

    def pre_validate(self) -> KrbError:
        for handler in self.pa_handlers:
            handler.pre_validate()

    def query_pre_validate(self):
        raise NotImplementedError

    def process_pre_auth(self):
        for handler in self.pa_handlers:
            handler.validate()

    def post_validate(self) -> KrbError:
        for handler in self.pa_handlers:
            handler.post_validate()

    def validate_ticket_request(self):
        pass

    def query_pre_execute(self):
        pass

    def execute(self):
        raise NotImplementedError

    def handle(self) -> KdcRep | KrbError:
        try:
            if self.ctx.message["pvno"] != 5:  # TODO: make constant
                raise KerberosError(code=KerberosError.Code.KDC_ERR_BAD_PVNO)
            self.pre_validate()
            self.query_pre_validate()
            self.process_pre_auth()
            self.post_validate()
            self.validate_ticket_request()
            self.query_pre_execute()
            return self.execute()
        except KerberosError as exc:
            return exc.to_krberror(
                realm=self.ctx.realm.name,
                crealm=self.ctx.realm.name,  # TODO: use crealm
                cname=self.ctx.cname,
                sname=self.ctx.sname,
            )


class AsMessageHandler(MessageHandler):
    PA_HANDLERS = [
        PaEncTimestampHandler,
        PaEtypeInfo2,
    ]

    def execute(self) -> KdcRep | KrbError:
        if not self.ctx.preauth_satisfied:
            raise KerberosError(
                code=KerberosError.Code.KDC_ERR_PREAUTH_REQUIRED,
                context={
                    "e-data": self.ctx.pa_data.to_bytes(),
                },
            )

        key = EncryptionKey.from_values(
            keytype=self.ctx.encrypted_part_enctype.ENC_TYPE.value,
            keyvalue=self.ctx.encrypted_part_key,
        )

        transited = TransitedEncoding.from_values(
            contents=bytes(),
            **{"tr-type": 1},
        )

        enc_ticket_part = EncTicketPart.from_values(
            key=key,
            crealm=self.ctx.realm.name,
            cname=self.ctx.cname,
            transited=transited,
            authtime=now(),
            starttime=now(),  # TODO: handle postdated
            endtime=str(self.ctx.message["req-body"]["till"]), # TODO: bound, time in the past, after from
        )
        # enc_ticket_part["renew-till"] = now() # TODO
        enc_ticket_part["flags"]["initial"] = True
        enc_ticket_part["flags"]["pre-authent"] = True

        # TODO: handle empty addresses policy
       #if "addresses" in self.ctx.message["req-body"]:
       #    enc_ticket_part.set_value(
       #        "caddr",
       #        self.ctx.message["req-body"]["addresses"],
       #    )
       #if "authorization-data" in self.ctx.message["req-body"]:
       #    enc_ticket_part.set_value(
       #        "authorization-data",
       #        self.ctx.message["req-body"]["authorization-data"],
       #    )

        ticket_enc_part = EncryptedData.from_values(
            etype=self.ctx.encrypted_part_enctype.ENC_TYPE.value,
            kvno=self.ctx.realm.kvno,
            cipher=self.ctx.encrypted_part_enctype.encrypt_message(
                key=self.ctx.realm.keys[self.ctx.encrypted_part_enctype.ENC_TYPE],
                message=enc_ticket_part.to_bytes(),
                usage=KeyUsageNumbers.KDC_REP_TICKET.value,
            ),
        )

        ticket = Ticket.from_values(
            realm=self.ctx.realm.name,
            sname=self.ctx.sname,
            **{
                "enc-part": ticket_enc_part,
                "tkt-vno": 5,  # make constant
            },
        )

        enc_as_rep_part = EncAsRepPart.from_values(
            nonce=int(self.ctx.message["req-body"]["nonce"]),
            srealm=self.ctx.realm.name,
            sname=self.ctx.sname,
        )
        # enc_as_rep_part["last-req"] = []
        for k in ("authtime", "starttime", "endtime", "key", "flags"): # TODO: "renew-till", "caddr"
            enc_as_rep_part.set_value(k, enc_ticket_part[k])

        #raise ValueError(enc_as_rep_part["flags"])
        #self.ctx.message["req-body"]["kdc-options"]["forwardable"] = True
        #raise ValueError(self.ctx.message["req-body"]["kdc-options"]["forwardable"])


        enc_part = EncryptedData()
        enc_part["etype"] = self.ctx.encrypted_part_enctype.ENC_TYPE.value
        enc_part["kvno"] = self.ctx.encrypted_part_kvno
        enc_part["cipher"] = self.ctx.encrypted_part_enctype.encrypt_message(
            key=self.ctx.encrypted_part_key,
            message=enc_as_rep_part.to_bytes(),
            usage=KeyUsageNumbers.AS_REP_ENCPART.value,
        )

        rep = AsRep.from_values(
            pvno=5,  # TODO: make constant
            crealm=self.ctx.realm.name,
            cname=self.ctx.cname,
            ticket=ticket,
            **{
                "msg-type": ApplicationTag.AS_REP.value,
                "enc-part": enc_part,
            },
        )
        if self.ctx.pa_data:
           rep.set_value("padata", self.ctx.pa_data)

        return rep

    def query_pre_validate(self):
        self.ctx.realm = KerberosRealm.objects.filter(
            name=self.ctx.message["req-body"]["realm"]
        ).first()
        if not self.ctx.realm:
            raise KerberosError("realm not found")

        self.ctx.user = User.objects.filter(
            username=self.ctx.message["req-body"]["cname"].to_string(),
        ).first()
        if not self.ctx.user:
            raise KerberosError(code=KerberosError.Code.KDC_ERR_C_PRINCIPAL_UNKNOWN)

        tgs_name = PrincipalName.from_components(
            name_type=PrincipalNameType.NT_SRV_INST,
            name=["krbtgt", self.ctx.realm.name],
        )
        if self.ctx.sname != tgs_name:
            self.ctx.provider = KerberosProvider.objects.filter(
                service_principal_name=self.ctx.message["req-body"]["sname"].to_string()
            ).first()
            if not self.ctx.provider:
                raise KerberosError(code=KerberosError.Code.KDC_ERR_S_PRINCIPAL_UNKNOWN)

    def query_pre_execute(self):
        # TODO: check flags and policy
        pass


@method_decorator(csrf_exempt, name="dispatch")
class KdcProxyView(View):
    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        try:
            proxy_message = KdcProxyMessage.from_bytes(request.body)
            expected_length = int.from_bytes(proxy_message["message"][:4])
            real_length = len(proxy_message["message"][4:])
            if real_length != expected_length:
                raise ValueError(
                    f"Mismatched message length: expected: {expected_length} got {real_length}"
                )
            message = KdcReq.from_bytes(proxy_message["message"][4:])
        except Exception as exc:
            raise SuspiciousOperation from exc

        ctx = Context(
            request=request,
            message=message,
        )

        if isinstance(message, AsReq):
            rep = AsMessageHandler(ctx).handle()
        if isinstance(message, TgsReq):
            # return TgsMessageHandler(ctx).handle()
            raise NotImplementedError

        content = rep.to_bytes()
        response = KdcProxyMessage()
        response["message"] = len(content).to_bytes(4, byteorder="big") + content

        return HttpResponse(
            response.to_bytes(),
            content_type="application/kerberos",
        )
