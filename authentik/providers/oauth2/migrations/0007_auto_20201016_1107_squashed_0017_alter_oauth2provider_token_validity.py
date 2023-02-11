# Generated by Django 3.2.8 on 2021-10-10 16:24

import django.db.models.deletion
from django.apps.registry import Apps
from django.db import migrations, models

import authentik.lib.utils.time

scope_uid_map = {
    "openid": "goauthentik.io/providers/oauth2/scope-openid",
    "email": "goauthentik.io/providers/oauth2/scope-email",
    "profile": "goauthentik.io/providers/oauth2/scope-profile",
    "ak_proxy": "goauthentik.io/providers/proxy/scope-proxy",
}


def set_managed_flag(apps: Apps, schema_editor):
    ScopeMapping = apps.get_model("authentik_providers_oauth2", "ScopeMapping")
    db_alias = schema_editor.connection.alias
    for mapping in ScopeMapping.objects.using(db_alias).filter(name__startswith="Autogenerated "):
        mapping.managed = scope_uid_map[mapping.scope_name]
        mapping.save()


class Migration(migrations.Migration):
    replaces = [
        ("authentik_providers_oauth2", "0007_auto_20201016_1107"),
        ("authentik_providers_oauth2", "0008_oauth2provider_issuer_mode"),
        ("authentik_providers_oauth2", "0009_remove_oauth2provider_response_type"),
        ("authentik_providers_oauth2", "0010_auto_20201227_1804"),
        ("authentik_providers_oauth2", "0011_managed"),
        ("authentik_providers_oauth2", "0012_oauth2provider_access_code_validity"),
        ("authentik_providers_oauth2", "0013_alter_authorizationcode_nonce"),
        ("authentik_providers_oauth2", "0014_alter_oauth2provider_rsa_key"),
        ("authentik_providers_oauth2", "0015_auto_20210703_1313"),
        ("authentik_providers_oauth2", "0016_alter_authorizationcode_nonce"),
        ("authentik_providers_oauth2", "0017_alter_oauth2provider_token_validity"),
    ]

    dependencies = [
        ("authentik_core", "0017_managed"),
        ("authentik_crypto", "0002_create_self_signed_kp"),
        ("authentik_providers_oauth2", "0006_remove_oauth2provider_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="refreshtoken",
            options={"verbose_name": "OAuth2 Token", "verbose_name_plural": "OAuth2 Tokens"},
        ),
        migrations.AddField(
            model_name="oauth2provider",
            name="issuer_mode",
            field=models.TextField(
                choices=[
                    ("global", "Same identifier is used for all providers"),
                    (
                        "per_provider",
                        "Each provider has a different issuer, based on the application slug.",
                    ),
                ],
                default="per_provider",
                help_text="Configure how the issuer field of the ID Token should be filled.",
            ),
        ),
        migrations.RemoveField(
            model_name="oauth2provider",
            name="response_type",
        ),
        migrations.AlterField(
            model_name="refreshtoken",
            name="access_token",
            field=models.TextField(verbose_name="Access Token"),
        ),
        migrations.RunPython(
            code=set_managed_flag,
        ),
        migrations.AddField(
            model_name="oauth2provider",
            name="access_code_validity",
            field=models.TextField(
                default="minutes=1",
                help_text=(
                    "Access codes not valid on or after current time + this value (Format:"
                    " hours=1;minutes=2;seconds=3)."
                ),
                validators=[authentik.lib.utils.time.timedelta_string_validator],
            ),
        ),
        migrations.AlterField(
            model_name="authorizationcode",
            name="nonce",
            field=models.TextField(blank=True, default="", verbose_name="Nonce"),
        ),
        migrations.AlterField(
            model_name="oauth2provider",
            name="rsa_key",
            field=models.ForeignKey(
                help_text=(
                    "Key used to sign the tokens. Only required when JWT Algorithm is set to RS256."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authentik_crypto.certificatekeypair",
                verbose_name="RSA Key",
            ),
        ),
        migrations.AddField(
            model_name="authorizationcode",
            name="revoked",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="refreshtoken",
            name="revoked",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="authorizationcode",
            name="nonce",
            field=models.TextField(default=None, null=True, verbose_name="Nonce"),
        ),
        migrations.AlterField(
            model_name="oauth2provider",
            name="token_validity",
            field=models.TextField(
                default="days=30",
                help_text=(
                    "Tokens not valid on or after current time + this value (Format:"
                    " hours=1;minutes=2;seconds=3)."
                ),
                validators=[authentik.lib.utils.time.timedelta_string_validator],
            ),
        ),
    ]
