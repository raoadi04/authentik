# Generated by Django 4.0.4 on 2022-05-23 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "authentik_sources_oauth",
            "0007_oauthsource_oidc_jwks_oauthsource_oidc_jwks_url_and_more",
        ),
        ("authentik_crypto", "0003_certificatekeypair_managed"),
        ("authentik_providers_oauth2", "0010_alter_oauth2provider_verification_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="oauth2provider",
            name="jwks_sources",
            field=models.ManyToManyField(
                blank=True,
                default=None,
                related_name="oauth2_providers",
                to="authentik_sources_oauth.oauthsource",
                verbose_name="Any JWT signed by the JWK of the selected source can be used to authenticate.",
            ),
        ),
        migrations.AlterField(
            model_name="oauth2provider",
            name="verification_keys",
            field=models.ManyToManyField(
                blank=True,
                default=None,
                help_text="JWTs created with the configured certificates can authenticate with this provider.",
                related_name="oauth2_providers",
                to="authentik_crypto.certificatekeypair",
                verbose_name="Allowed certificates for JWT-based client_credentials",
            ),
        ),
    ]
