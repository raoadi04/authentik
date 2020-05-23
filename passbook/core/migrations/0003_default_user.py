# Generated by Django 3.0.6 on 2020-05-23 16:40

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def create_default_user(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    # User = apps.get_model("passbook_core", "User")
    from passbook.core.models import User

    pbadmin = User.objects.create(
        username="pbadmin", email="root@localhost",  # password="pbadmin"
    )
    pbadmin.set_password("pbadmin")  # noqa # nosec
    pbadmin.is_superuser = True
    pbadmin.save()


class Migration(migrations.Migration):

    dependencies = [
        ("passbook_core", "0002_auto_20200523_1133"),
    ]

    operations = [
        migrations.RunPython(create_default_user),
    ]
