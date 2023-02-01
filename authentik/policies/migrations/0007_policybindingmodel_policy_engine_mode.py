# Generated by Django 3.1.7 on 2021-03-31 08:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_policies", "0006_auto_20210329_1334"),
    ]

    operations = [
        # Create field with default as all for backwards compat
        migrations.AddField(
            model_name="policybindingmodel",
            name="policy_engine_mode",
            field=models.TextField(
                choices=[
                    ("all", "ALL, all policies must pass"),
                    ("any", "ANY, any policy must pass"),
                ],
                default="all",
            ),
        ),
        # Set default for new objects to any
        migrations.AlterField(
            model_name="policybindingmodel",
            name="policy_engine_mode",
            field=models.TextField(
                choices=[
                    ("all", "ALL, all policies must pass"),
                    ("any", "ANY, any policy must pass"),
                ],
                default="any",
            ),
        ),
    ]
