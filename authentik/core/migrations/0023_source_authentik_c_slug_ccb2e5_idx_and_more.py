# Generated by Django 4.1.2 on 2022-10-19 18:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_core", "0022_alter_group_parent"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="source",
            index=models.Index(fields=["slug"], name="authentik_c_slug_ccb2e5_idx"),
        ),
        migrations.AddIndex(
            model_name="source",
            index=models.Index(fields=["name"], name="authentik_c_name_affae6_idx"),
        ),
    ]
