# Generated by Django 4.0.4 on 2022-05-24 19:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_stages_authenticator_sms", "0003_smsdevice_last_used_on"),
    ]

    operations = [
        migrations.AddField(
            model_name="authenticatorsmsstage",
            name="verify_only",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "When enabled, the Phone number is only used during enrollment to verify the"
                    " users authenticity. Only a hash of the phone number is saved to ensure it is"
                    " not reused in the future."
                ),
            ),
        ),
        migrations.AlterUniqueTogether(
            name="smsdevice",
            unique_together={("stage", "phone_number")},
        ),
    ]
