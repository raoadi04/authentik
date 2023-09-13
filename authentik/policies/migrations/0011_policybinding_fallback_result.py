# Generated by Django 4.2.5 on 2023-09-12 10:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_policies", "0010_alter_policy_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="policybinding",
            name="failure_result",
            field=models.BooleanField(
                default=False, help_text="Fallback result if the Policy execution fails."
            ),
        ),
    ]
