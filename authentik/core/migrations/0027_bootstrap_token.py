# Generated by Django 3.2.5 on 2021-08-11 19:40
from os import environ

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def create_default_user_token(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    # We have to use a direct import here, otherwise we get an object manager error
    from authentik.core.models import Token, TokenIntents, User

    db_alias = schema_editor.connection.alias

    akadmin = User.objects.using(db_alias).filter(username="akadmin")
    if not akadmin.exists():
        return
    if "AK_ADMIN_TOKEN" not in environ:
        return
    Token.objects.using(db_alias).create(
        identifier="authentik-boostrap-token",
        user=akadmin.first(),
        intent=TokenIntents.INTENT_API,
        expiring=False,
        key=environ["AK_ADMIN_TOKEN"],
    )


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_core", "0026_alter_application_meta_icon"),
    ]

    operations = [
        migrations.RunPython(create_default_user_token),
    ]
