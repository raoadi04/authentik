# Generated by Django 4.1.2 on 2022-10-19 19:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "authentik_policies_reputation",
            "0003_reputation_delete_ipreputation_delete_userreputation",
        ),
    ]

    operations = [
        migrations.AddIndex(
            model_name="reputationpolicy",
            index=models.Index(fields=["policy_ptr_id"], name="authentik_p_policy__8f0d70_idx"),
        ),
    ]
