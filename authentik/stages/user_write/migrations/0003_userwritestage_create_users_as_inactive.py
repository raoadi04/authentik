# Generated by Django 3.2.4 on 2021-06-28 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_stages_user_write", "0002_auto_20200918_1653"),
    ]

    operations = [
        migrations.AddField(
            model_name="userwritestage",
            name="create_users_as_inactive",
            field=models.BooleanField(
                default=False,
                help_text="When set, newly created users are inactive and cannot login.",
            ),
        ),
    ]
