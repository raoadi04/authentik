# Generated by Django 4.1.7 on 2023-02-25 15:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_flows", "0024_flow_authentication"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flowstagebinding",
            name="evaluate_on_plan",
            field=models.BooleanField(
                default=False, help_text="Evaluate policies during the Flow planning process."
            ),
        ),
        migrations.AlterField(
            model_name="flowstagebinding",
            name="re_evaluate_policies",
            field=models.BooleanField(
                default=True, help_text="Evaluate policies when the Stage is present to the user."
            ),
        ),
    ]
