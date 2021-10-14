# Generated by Django 3.2.8 on 2021-10-10 16:16

from os import environ

import django.db.models.deletion
from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

import authentik.core.models


def create_default_user(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    # We have to use a direct import here, otherwise we get an object manager error
    from authentik.core.models import User

    db_alias = schema_editor.connection.alias

    akadmin, _ = User.objects.using(db_alias).get_or_create(
        username="akadmin", email="root@localhost", name="authentik Default Admin"
    )
    if "TF_BUILD" in environ or "AK_ADMIN_PASS" in environ or settings.TEST:
        akadmin.set_password(environ.get("AK_ADMIN_PASS", "akadmin"), signal=False)  # noqa # nosec
    else:
        akadmin.set_unusable_password()
    akadmin.save()


def create_default_admin_group(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    db_alias = schema_editor.connection.alias
    Group = apps.get_model("authentik_core", "Group")
    User = apps.get_model("authentik_core", "User")

    # Creates a default admin group
    group, _ = Group.objects.using(db_alias).get_or_create(
        is_superuser=True,
        defaults={
            "name": "authentik Admins",
        },
    )
    group.users.set(User.objects.filter(username="akadmin"))
    group.save()


class Migration(migrations.Migration):

    replaces = [
        ("authentik_core", "0002_auto_20200523_1133"),
        ("authentik_core", "0003_default_user"),
        ("authentik_core", "0004_auto_20200703_2213"),
        ("authentik_core", "0005_token_intent"),
        ("authentik_core", "0006_auto_20200709_1608"),
        ("authentik_core", "0007_auto_20200815_1841"),
        ("authentik_core", "0008_auto_20200824_1532"),
        ("authentik_core", "0009_group_is_superuser"),
        ("authentik_core", "0010_auto_20200917_1021"),
        ("authentik_core", "0011_provider_name_temp"),
    ]

    dependencies = [
        ("authentik_core", "0001_initial"),
        ("authentik_flows", "0003_auto_20200523_1133"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="application",
            name="skip_authorization",
        ),
        migrations.AddField(
            model_name="source",
            name="authentication_flow",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text="Flow to use when authenticating existing users.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="source_authentication",
                to="authentik_flows.flow",
            ),
        ),
        migrations.AddField(
            model_name="source",
            name="enrollment_flow",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text="Flow to use when enrolling new users.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="source_enrollment",
                to="authentik_flows.flow",
            ),
        ),
        migrations.AddField(
            model_name="provider",
            name="authorization_flow",
            field=models.ForeignKey(
                help_text="Flow used when authorizing this provider.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="provider_authorization",
                to="authentik_flows.flow",
            ),
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_superuser",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_staff",
        ),
        migrations.RunPython(
            code=create_default_user,
        ),
        migrations.AddField(
            model_name="user",
            name="is_superuser",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name="application",
            options={"verbose_name": "Application", "verbose_name_plural": "Applications"},
        ),
        migrations.AlterModelOptions(
            name="user",
            options={
                "permissions": (("reset_user_password", "Reset Password"),),
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
        ),
        migrations.AddField(
            model_name="token",
            name="intent",
            field=models.TextField(
                choices=[("verification", "Intent Verification"), ("api", "Intent Api")],
                default="verification",
            ),
        ),
        migrations.AlterField(
            model_name="source",
            name="slug",
            field=models.SlugField(help_text="Internal source name, used in URLs.", unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="first name"),
        ),
        migrations.RemoveField(
            model_name="user",
            name="groups",
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_superuser",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_staff",
        ),
        migrations.AddField(
            model_name="user",
            name="pb_groups",
            field=models.ManyToManyField(related_name="users", to="authentik_core.Group"),
        ),
        migrations.AddField(
            model_name="group",
            name="is_superuser",
            field=models.BooleanField(
                default=False, help_text="Users added to this group will be superusers."
            ),
        ),
        migrations.RunPython(
            code=create_default_admin_group,
        ),
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", authentik.core.models.UserManager()),
            ],
        ),
        migrations.AlterModelOptions(
            name="user",
            options={
                "permissions": (
                    ("reset_user_password", "Reset Password"),
                    ("impersonate", "Can impersonate other users"),
                ),
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
        ),
        migrations.AddField(
            model_name="provider",
            name="name_temp",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
