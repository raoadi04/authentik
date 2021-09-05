# Generated by Django 3.2.5 on 2021-07-13 11:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_crypto", "0002_create_self_signed_kp"),
        ("authentik_providers_ldap", "0002_ldapprovider_search_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="ldapprovider",
            name="certificate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="authentik_crypto.certificatekeypair",
            ),
        ),
        migrations.AddField(
            model_name="ldapprovider",
            name="tls_server_name",
            field=models.TextField(blank=True, default=""),
        ),
    ]
