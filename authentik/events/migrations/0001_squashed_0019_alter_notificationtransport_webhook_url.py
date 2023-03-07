# Generated by Django 3.2.8 on 2021-10-10 16:01

import uuid
from datetime import timedelta

import django.db.models.deletion
from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

import authentik.events.models
import authentik.lib.models
from authentik.events.models import EventAction, NotificationSeverity, TransportMode
from authentik.lib.migrations import progress_bar


def convert_user_to_json(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    Event = apps.get_model("authentik_events", "Event")

    db_alias = schema_editor.connection.alias
    for event in Event.objects.using(db_alias).all():
        event.delete()
        # Because event objects cannot be updated, we have to re-create them
        event.pk = None
        event.user_json = authentik.events.models.get_user(event.user) if event.user else {}
        event._state.adding = True
        event.save()


def token_view_to_secret_view(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    from authentik.events.models import EventAction

    db_alias = schema_editor.connection.alias
    Event = apps.get_model("authentik_events", "Event")

    events = Event.objects.using(db_alias).filter(action="token_view")

    for event in events:
        event.context["secret"] = event.context.pop("token")
        event.action = EventAction.SECRET_VIEW

    Event.objects.using(db_alias).bulk_update(events, ["context", "action"])


def update_expires(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    db_alias = schema_editor.connection.alias
    Event = apps.get_model("authentik_events", "event")
    all_events = Event.objects.using(db_alias).all()
    if all_events.count() < 1:
        return

    print("\nAdding expiry to events, this might take a couple of minutes...")
    for event in progress_bar(all_events):
        event.expires = event.created + timedelta(days=365)
        event.save()


class Migration(migrations.Migration):
    replaces = [
        ("authentik_events", "0001_initial"),
        ("authentik_events", "0002_auto_20200918_2116"),
        ("authentik_events", "0003_auto_20200917_1155"),
        ("authentik_events", "0004_auto_20200921_1829"),
        ("authentik_events", "0005_auto_20201005_2139"),
        ("authentik_events", "0006_auto_20201017_2024"),
        ("authentik_events", "0007_auto_20201215_0939"),
        ("authentik_events", "0008_auto_20201220_1651"),
        ("authentik_events", "0009_auto_20201227_1210"),
        ("authentik_events", "0010_notification_notificationtransport_notificationrule"),
        ("authentik_events", "0011_notification_rules_default_v1"),
        ("authentik_events", "0012_auto_20210202_1821"),
        ("authentik_events", "0013_auto_20210209_1657"),
        ("authentik_events", "0014_expiry"),
        ("authentik_events", "0015_alter_event_action"),
        ("authentik_events", "0016_add_tenant"),
        ("authentik_events", "0017_alter_event_action"),
        ("authentik_events", "0018_auto_20210911_2217"),
        ("authentik_events", "0019_alter_notificationtransport_webhook_url"),
    ]

    initial = True

    dependencies = [
        ("authentik_policies", "0004_policy_execution_logging"),
        ("authentik_core", "0016_auto_20201202_2234"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("authentik_policies_event_matcher", "0003_auto_20210110_1907"),
        ("authentik_core", "0028_alter_token_intent"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "event_uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "action",
                    models.TextField(
                        choices=[
                            ("LOGIN", "login"),
                            ("LOGIN_FAILED", "login_failed"),
                            ("LOGOUT", "logout"),
                            ("AUTHORIZE_APPLICATION", "authorize_application"),
                            ("SUSPICIOUS_REQUEST", "suspicious_request"),
                            ("SIGN_UP", "sign_up"),
                            ("PASSWORD_RESET", "password_reset"),
                            ("INVITE_CREATED", "invitation_created"),
                            ("INVITE_USED", "invitation_used"),
                            ("IMPERSONATION_STARTED", "impersonation_started"),
                            ("IMPERSONATION_ENDED", "impersonation_ended"),
                            ("CUSTOM", "custom"),
                        ]
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("app", models.TextField()),
                ("context", models.JSONField(blank=True, default=dict)),
                ("client_ip", models.GenericIPAddressField(null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("user_json", models.JSONField(default=dict)),
            ],
            options={
                "verbose_name": "Event",
                "verbose_name_plural": "Events",
            },
        ),
        migrations.RunPython(
            code=convert_user_to_json,
        ),
        migrations.RemoveField(
            model_name="event",
            name="user",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="user_json",
            new_name="user",
        ),
        migrations.RemoveField(
            model_name="event",
            name="date",
        ),
        migrations.CreateModel(
            name="NotificationTransport",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(unique=True)),
                (
                    "mode",
                    models.TextField(
                        choices=[
                            ("webhook", "Generic Webhook"),
                            ("webhook_slack", "Slack Webhook (Slack/Discord)"),
                            ("email", "Email"),
                        ]
                    ),
                ),
                ("webhook_url", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Notification Transport",
                "verbose_name_plural": "Notification Transports",
            },
        ),
        migrations.CreateModel(
            name="NotificationRule",
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
                    "severity",
                    models.TextField(
                        choices=[("notice", "Notice"), ("warning", "Warning"), ("alert", "Alert")],
                        default="notice",
                        help_text=(
                            "Controls which severity level the created notifications will have."
                        ),
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        help_text=(
                            "Define which group of users this notification should be sent and shown"
                            " to. If left empty, Notification won't ben sent."
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="authentik_core.group",
                    ),
                ),
                (
                    "transports",
                    models.ManyToManyField(
                        help_text=(
                            "Select which transports should be used to notify the user. If none are"
                            " selected, the notification will only be shown in the authentik UI."
                        ),
                        to="authentik_events.NotificationTransport",
                        blank=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification Rule",
                "verbose_name_plural": "Notification Rules",
            },
            bases=("authentik_policies.policybindingmodel",),
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "severity",
                    models.TextField(
                        choices=[("notice", "Notice"), ("warning", "Warning"), ("alert", "Alert")]
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
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
        migrations.AddField(
            model_name="notificationtransport",
            name="send_once",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Only send notification once, for example when sending a webhook into a chat"
                    " channel."
                ),
            ),
        ),
        migrations.RunPython(
            code=token_view_to_secret_view,
        ),
        migrations.AddField(
            model_name="event",
            name="expires",
            field=models.DateTimeField(default=authentik.events.models.default_event_duration),
        ),
        migrations.AddField(
            model_name="event",
            name="expiring",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(
            code=update_expires,
        ),
        migrations.AddField(
            model_name="event",
            name="tenant",
            field=models.JSONField(blank=True, default=authentik.events.models.default_tenant),
        ),
        migrations.AlterField(
            model_name="event",
            name="action",
            field=models.TextField(
                choices=[
                    ("login", "Login"),
                    ("login_failed", "Login Failed"),
                    ("logout", "Logout"),
                    ("user_write", "User Write"),
                    ("suspicious_request", "Suspicious Request"),
                    ("password_set", "Password Set"),
                    ("secret_view", "Secret View"),
                    ("secret_rotate", "Secret Rotate"),
                    ("invitation_used", "Invite Used"),
                    ("authorize_application", "Authorize Application"),
                    ("source_linked", "Source Linked"),
                    ("impersonation_started", "Impersonation Started"),
                    ("impersonation_ended", "Impersonation Ended"),
                    ("flow_execution", "Flow Execution"),
                    ("policy_execution", "Policy Execution"),
                    ("policy_exception", "Policy Exception"),
                    ("property_mapping_exception", "Property Mapping Exception"),
                    ("system_task_execution", "System Task Execution"),
                    ("system_task_exception", "System Task Exception"),
                    ("system_exception", "System Exception"),
                    ("configuration_error", "Configuration Error"),
                    ("model_created", "Model Created"),
                    ("model_updated", "Model Updated"),
                    ("model_deleted", "Model Deleted"),
                    ("email_sent", "Email Sent"),
                    ("update_available", "Update Available"),
                    ("custom_", "Custom Prefix"),
                ]
            ),
        ),
        migrations.CreateModel(
            name="NotificationWebhookMapping",
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
                "verbose_name": "Notification Webhook Mapping",
                "verbose_name_plural": "Notification Webhook Mappings",
            },
            bases=("authentik_core.propertymapping",),
        ),
        migrations.AddField(
            model_name="notificationtransport",
            name="webhook_mapping",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to="authentik_events.notificationwebhookmapping",
            ),
        ),
        migrations.AlterField(
            model_name="notificationtransport",
            name="webhook_url",
            field=models.TextField(
                blank=True, validators=[authentik.lib.models.DomainlessURLValidator()]
            ),
        ),
    ]
