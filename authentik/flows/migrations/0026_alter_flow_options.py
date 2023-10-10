# Generated by Django 4.2.6 on 2023-10-10 17:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_flows", "0025_alter_flowstagebinding_evaluate_on_plan_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="flow",
            options={
                "permissions": [
                    ("export_flow", "Can export a Flow"),
                    ("inspect_flow", "Can inspect a Flow's execution"),
                    ("view_flow_cache", "View Flow's cache metrics"),
                    ("clear_flow_cache", "Clear Flow's cache metrics"),
                ],
                "verbose_name": "Flow",
                "verbose_name_plural": "Flows",
            },
        ),
    ]
