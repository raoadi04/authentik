# Generated by Django 5.0.5 on 2024-05-08 00:02

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("authentik_core", "0035_alter_group_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MicrosoftEntraProviderMapping",
            fields=[
                (
                    "propertymapping_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="authentik_core.propertymapping",
                    ),
                ),
            ],
            options={
                "verbose_name": "Microsoft Entra Provider Mapping",
                "verbose_name_plural": "Microsoft Entra Provider Mappings",
            },
            bases=("authentik_core.propertymapping",),
        ),
        migrations.CreateModel(
            name="MicrosoftEntraProvider",
            fields=[
                (
                    "provider_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="authentik_core.provider",
                    ),
                ),
                ("client_id", models.TextField()),
                ("client_secret", models.TextField()),
                ("tenant_id", models.TextField()),
                ("exclude_users_service_account", models.BooleanField(default=False)),
                (
                    "user_delete_action",
                    models.TextField(
                        choices=[
                            ("do_nothing", "Do Nothing"),
                            ("delete", "Delete"),
                            ("suspend", "Suspend"),
                        ],
                        default="delete",
                    ),
                ),
                (
                    "group_delete_action",
                    models.TextField(
                        choices=[
                            ("do_nothing", "Do Nothing"),
                            ("delete", "Delete"),
                            ("suspend", "Suspend"),
                        ],
                        default="delete",
                    ),
                ),
                (
                    "filter_group",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to="authentik_core.group",
                    ),
                ),
                (
                    "property_mappings_group",
                    models.ManyToManyField(
                        blank=True,
                        default=None,
                        help_text="Property mappings used for group creation/updating.",
                        to="authentik_core.propertymapping",
                    ),
                ),
            ],
            options={
                "verbose_name": "Microsoft Entra Provider",
                "verbose_name_plural": "Microsoft Entra Providers",
            },
            bases=("authentik_core.provider", models.Model),
        ),
        migrations.CreateModel(
            name="MicrosoftEntraProviderGroup",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("microsoft_id", models.TextField()),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="authentik_core.group"
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentik_providers_microsoft_entra.microsoftentraprovider",
                    ),
                ),
            ],
            options={
                "unique_together": {("microsoft_id", "group", "provider")},
            },
        ),
        migrations.CreateModel(
            name="MicrosoftEntraProviderUser",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("microsoft_id", models.TextField()),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentik_providers_microsoft_entra.microsoftentraprovider",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "unique_together": {("microsoft_id", "user", "provider")},
            },
        ),
    ]
