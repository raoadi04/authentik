# Generated by Django 4.0.5 on 2022-06-14 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_stages_user_write", "0004_userwritestage_create_users_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="userwritestage",
            name="user_path_template",
            field=models.TextField(default="", blank=True),
        ),
    ]
