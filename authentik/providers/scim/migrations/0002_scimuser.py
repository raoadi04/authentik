# Generated by Django 4.1.7 on 2023-03-02 15:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("authentik_providers_scim", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SCIMUser",
            fields=[
                ("id", models.TextField(primary_key=True, serialize=False)),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentik_providers_scim.scimprovider",
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
                "unique_together": {("id", "user", "provider")},
            },
        ),
    ]
