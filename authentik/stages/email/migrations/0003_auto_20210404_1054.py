# Generated by Django 3.1.7 on 2021-04-04 10:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_stages_email", "0002_emailstage_use_global_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailstage",
            name="template",
            field=models.TextField(default="email/password_reset.html"),
        ),
    ]
