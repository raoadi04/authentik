# Generated by Django 3.0.6 on 2020-05-19 22:08

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CertificateKeyPair",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "kp_uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField()),
                (
                    "certificate_data",
                    models.TextField(help_text="PEM-encoded Certificate data"),
                ),
                (
                    "key_data",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text=(
                            "Optional Private Key. If this is set, you can use this keypair for"
                            " encryption."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Certificate-Key Pair",
                "verbose_name_plural": "Certificate-Key Pairs",
            },
        ),
    ]
