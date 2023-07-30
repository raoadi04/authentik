# Generated by Django 4.2.3 on 2023-07-30 13:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_outposts", "0020_alter_outpost_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="outpost",
            name="type",
            field=models.TextField(
                choices=[
                    ("proxy", "Proxy"),
                    ("ldap", "Ldap"),
                    ("radius", "Radius"),
                    ("kerberos", "Kerberos"),
                ],
                default="proxy",
            ),
        ),
    ]
