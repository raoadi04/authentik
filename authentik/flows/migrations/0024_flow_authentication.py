# Generated by Django 4.1.3 on 2022-11-30 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_flows", "0023_flow_denied_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="flow",
            name="authentication",
            field=models.TextField(
                choices=[
                    ("none", "None"),
                    ("require_authenticated", "Require Authenticated"),
                    ("require_unauthenticated", "Require Unauthenticated"),
                    ("require_superuser", "Require Superuser"),
                ],
                default="none",
                help_text="Required level of authentication and authorization to access a flow.",
            ),
        ),
    ]
