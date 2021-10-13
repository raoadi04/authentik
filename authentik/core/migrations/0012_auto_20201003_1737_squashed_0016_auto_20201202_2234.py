# Generated by Django 3.2.8 on 2021-10-12 15:36

from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

import authentik.core.models


def set_default_token_key(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    db_alias = schema_editor.connection.alias
    Token = apps.get_model("authentik_core", "Token")

    for token in Token.objects.using(db_alias).all():
        token.key = token.pk.hex
        token.save()


class Migration(migrations.Migration):

    replaces = [
        ("authentik_core", "0012_auto_20201003_1737"),
        ("authentik_core", "0013_auto_20201003_2132"),
        ("authentik_core", "0014_auto_20201018_1158"),
        ("authentik_core", "0015_application_icon"),
        ("authentik_core", "0016_auto_20201202_2234"),
    ]

    dependencies = [
        ("authentik_providers_saml", "0006_remove_samlprovider_name"),
        ("authentik_providers_oauth2", "0006_remove_oauth2provider_name"),
        ("authentik_core", "0011_provider_name_temp"),
    ]

    operations = [
        migrations.RenameField(
            model_name="provider",
            old_name="name_temp",
            new_name="name",
        ),
        migrations.AddField(
            model_name="token",
            name="identifier",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="token",
            name="intent",
            field=models.TextField(
                choices=[
                    ("verification", "Intent Verification"),
                    ("api", "Intent Api"),
                    ("recovery", "Intent Recovery"),
                ],
                default="verification",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="token",
            unique_together={("identifier", "user")},
        ),
        migrations.AddField(
            model_name="token",
            name="key",
            field=models.TextField(default=authentik.core.models.default_token_key),
        ),
        migrations.AlterUniqueTogether(
            name="token",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="token",
            name="identifier",
            field=models.SlugField(max_length=255),
        ),
        migrations.AddIndex(
            model_name="token",
            index=models.Index(fields=["key"], name="authentik_co_key_e45007_idx"),
        ),
        migrations.AddIndex(
            model_name="token",
            index=models.Index(fields=["identifier"], name="authentik_co_identif_1a34a8_idx"),
        ),
        migrations.RunPython(
            code=set_default_token_key,
        ),
        migrations.RemoveField(
            model_name="application",
            name="meta_icon_url",
        ),
        migrations.AddField(
            model_name="application",
            name="meta_icon",
            field=models.FileField(blank=True, default="", upload_to="application-icons/"),
        ),
        migrations.RemoveIndex(
            model_name="token",
            name="authentik_co_key_e45007_idx",
        ),
        migrations.RemoveIndex(
            model_name="token",
            name="authentik_co_identif_1a34a8_idx",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="pb_groups",
            new_name="ak_groups",
        ),
        migrations.AddIndex(
            model_name="token",
            index=models.Index(fields=["identifier"], name="authentik_c_identif_d9d032_idx"),
        ),
        migrations.AddIndex(
            model_name="token",
            index=models.Index(fields=["key"], name="authentik_c_key_f71355_idx"),
        ),
    ]
