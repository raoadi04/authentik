# Generated by Django 4.0.5 on 2022-06-04 06:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_core", "0019_application_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="open_in_new_tab",
            field=models.BooleanField(
                default=False, help_text="Open launch URL in a new browser tab or window."
            ),
        ),
    ]
