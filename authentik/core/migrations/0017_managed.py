# Generated by Django 3.1.4 on 2021-01-30 18:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_core", "0016_auto_20201202_2234"),
    ]

    operations = [
        migrations.AddField(
            model_name="propertymapping",
            name="managed",
            field=models.TextField(
                default=None,
                help_text=(
                    "Objects which are managed by authentik. These objects are created and updated"
                    " automatically. This is flag only indicates that an object can be overwritten"
                    " by migrations. You can still modify the objects via the API, but expect"
                    " changes to be overwritten in a later update."
                ),
                null=True,
                verbose_name="Managed by authentik",
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="managed",
            field=models.TextField(
                default=None,
                help_text=(
                    "Objects which are managed by authentik. These objects are created and updated"
                    " automatically. This is flag only indicates that an object can be overwritten"
                    " by migrations. You can still modify the objects via the API, but expect"
                    " changes to be overwritten in a later update."
                ),
                null=True,
                verbose_name="Managed by authentik",
                unique=True,
            ),
        ),
    ]
