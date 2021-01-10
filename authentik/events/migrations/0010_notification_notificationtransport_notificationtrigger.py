# Generated by Django 3.1.4 on 2021-01-10 14:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_policies", "0004_policy_execution_logging"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("authentik_core", "0016_auto_20201202_2234"),
        ("authentik_events", "0009_auto_20201227_1210"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationTransport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.TextField(unique=True)),
            ],
            options={
                "verbose_name": "Notification Transport",
                "verbose_name_plural": "Notification Transports",
            },
        ),
        migrations.CreateModel(
            name="NotificationTrigger",
            fields=[
                (
                    "policybindingmodel_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="authentik_policies.policybindingmodel",
                    ),
                ),
                ("name", models.TextField(unique=True)),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        help_text="Define which group of users this notification should be sent and shown to. If left empty, Notification won't ben sent.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="authentik_core.group",
                    ),
                ),
                (
                    "transport",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to="authentik_events.notificationtransport",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification Trigger",
                "verbose_name_plural": "Notification Triggers",
            },
            bases=("authentik_policies.policybindingmodel",),
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "severity",
                    models.TextField(
                        choices=[
                            ("notice", "Notice"),
                            ("warning", "Warning"),
                            ("alert", "Alert"),
                        ]
                    ),
                ),
                ("body", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("seen", models.BooleanField(default=False)),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="authentik_events.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
    ]
