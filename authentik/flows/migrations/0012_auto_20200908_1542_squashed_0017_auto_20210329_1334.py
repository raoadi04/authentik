# Generated by Django 3.2.8 on 2021-10-10 16:08

import django.db.models.deletion
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

import authentik.lib.models
from authentik.flows.models import FlowDesignation


def update_flow_designation(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    Flow = apps.get_model("authentik_flows", "Flow")
    db_alias = schema_editor.connection.alias

    for flow in Flow.objects.using(db_alias).all():
        if flow.designation == "stage_setup":
            flow.designation = FlowDesignation.STAGE_CONFIGURATION
            flow.save()


class Migration(migrations.Migration):

    replaces = [
        ("authentik_flows", "0012_auto_20200908_1542"),
        ("authentik_flows", "0013_auto_20200924_1605"),
        ("authentik_flows", "0014_auto_20200925_2332"),
        ("authentik_flows", "0015_flowstagebinding_evaluate_on_plan"),
        ("authentik_flows", "0016_auto_20201202_1307"),
        ("authentik_flows", "0017_auto_20210329_1334"),
    ]

    dependencies = [
        ("authentik_flows", "0011_flow_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flowstagebinding",
            name="stage",
            field=authentik.lib.models.InheritanceForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="authentik_flows.stage"
            ),
        ),
        migrations.AlterField(
            model_name="stage",
            name="name",
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name="flow",
            name="designation",
            field=models.CharField(
                choices=[
                    ("authentication", "Authentication"),
                    ("authorization", "Authorization"),
                    ("invalidation", "Invalidation"),
                    ("enrollment", "Enrollment"),
                    ("unenrollment", "Unrenollment"),
                    ("recovery", "Recovery"),
                    ("stage_configuration", "Stage Configuration"),
                ],
                max_length=100,
            ),
        ),
        migrations.RunPython(
            code=update_flow_designation,
        ),
        migrations.AlterModelOptions(
            name="flowstagebinding",
            options={
                "ordering": ["target", "order"],
                "verbose_name": "Flow Stage Binding",
                "verbose_name_plural": "Flow Stage Bindings",
            },
        ),
        migrations.AlterField(
            model_name="flowstagebinding",
            name="re_evaluate_policies",
            field=models.BooleanField(
                default=False,
                help_text="When this option is enabled, the planner will re-evaluate policies bound to this binding.",
            ),
        ),
        migrations.AlterField(
            model_name="flowstagebinding",
            name="re_evaluate_policies",
            field=models.BooleanField(
                default=False, help_text="Evaluate policies when the Stage is present to the user."
            ),
        ),
        migrations.AddField(
            model_name="flowstagebinding",
            name="evaluate_on_plan",
            field=models.BooleanField(
                default=True,
                help_text="Evaluate policies during the Flow planning process. Disable this for input-based policies.",
            ),
        ),
        migrations.AddField(
            model_name="flow",
            name="background",
            field=models.FileField(
                blank=True,
                default="../static/dist/assets/images/flow_background.jpg",
                help_text="Background shown during execution",
                upload_to="flow-backgrounds/",
            ),
        ),
        migrations.AlterField(
            model_name="flow",
            name="designation",
            field=models.CharField(
                choices=[
                    ("authentication", "Authentication"),
                    ("authorization", "Authorization"),
                    ("invalidation", "Invalidation"),
                    ("enrollment", "Enrollment"),
                    ("unenrollment", "Unrenollment"),
                    ("recovery", "Recovery"),
                    ("stage_configuration", "Stage Configuration"),
                ],
                help_text="Decides what this Flow is used for. For example, the Authentication flow is redirect to when an un-authenticated user visits authentik.",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="flow",
            name="slug",
            field=models.SlugField(help_text="Visible in the URL.", unique=True),
        ),
        migrations.AlterField(
            model_name="flow",
            name="title",
            field=models.TextField(help_text="Shown as the Title in Flow pages."),
        ),
        migrations.AlterModelOptions(
            name="flow",
            options={
                "permissions": [
                    ("export_flow", "Can export a Flow"),
                    ("view_flow_cache", "View Flow's cache metrics"),
                    ("clear_flow_cache", "Clear Flow's cache metrics"),
                ],
                "verbose_name": "Flow",
                "verbose_name_plural": "Flows",
            },
        ),
    ]
