# Generated by Django 4.0.4 on 2022-05-10 17:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_stages_authenticator_duo", "0002_default_setup_flow"),
    ]

    operations = [
        migrations.AddField(
            model_name="duodevice",
            name="last_t",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
