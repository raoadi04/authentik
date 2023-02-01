# Generated by Django 4.0.4 on 2022-05-30 18:08
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_events", "0001_squashed_0019_alter_notificationtransport_webhook_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationtransport",
            name="mode",
            field=models.TextField(
                choices=[
                    ("local", "authentik inbuilt notifications"),
                    ("webhook", "Generic Webhook"),
                    ("webhook_slack", "Slack Webhook (Slack/Discord)"),
                    ("email", "Email"),
                ],
                default="local",
            ),
        ),
        migrations.AlterModelOptions(
            name="notificationwebhookmapping",
            options={"verbose_name": "Webhook Mapping", "verbose_name_plural": "Webhook Mappings"},
        ),
    ]
