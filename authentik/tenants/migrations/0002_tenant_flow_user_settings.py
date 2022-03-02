# Generated by Django 4.0.2 on 2022-02-26 21:14

import django.db.models.deletion
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

from authentik.flows.models import FlowDesignation
from authentik.stages.identification.models import UserFields
from authentik.stages.password import BACKEND_APP_PASSWORD, BACKEND_INBUILT, BACKEND_LDAP

AUTHORIZATION_POLICY = """from authentik.lib.config import CONFIG
from authentik.core.models import (
    USER_ATTRIBUTE_CHANGE_EMAIL,
    USER_ATTRIBUTE_CHANGE_NAME,
    USER_ATTRIBUTE_CHANGE_USERNAME
)
prompt_data = request.context.get("prompt_data")

if not request.user.group_attributes().get(
    USER_ATTRIBUTE_CHANGE_EMAIL, CONFIG.y_bool("default_user_change_email", True)
):
    if prompt_data.get("email") != request.user.email:
        ak_message("Not allowed to change email address.")
        return False

if not request.user.group_attributes().get(
    USER_ATTRIBUTE_CHANGE_NAME, CONFIG.y_bool("default_user_change_name", True)
):
    if prompt_data.get("name") != request.user.name:
        ak_message("Not allowed to change name.")
        return False

if not request.user.group_attributes().get(
    USER_ATTRIBUTE_CHANGE_USERNAME, CONFIG.y_bool("default_user_change_username", True)
):
    if prompt_data.get("username") != request.user.username:
        ak_message("Not allowed to change username.")
        return False

return True
"""


def create_default_user_settings_flow(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    from authentik.stages.prompt.models import FieldTypes

    db_alias = schema_editor.connection.alias

    Tenant = apps.get_model("authentik_tenants", "Tenant")

    Flow = apps.get_model("authentik_flows", "Flow")
    FlowStageBinding = apps.get_model("authentik_flows", "FlowStageBinding")

    ExpressionPolicy = apps.get_model("authentik_policies_expression", "ExpressionPolicy")

    UserWriteStage = apps.get_model("authentik_stages_user_write", "UserWriteStage")
    PromptStage = apps.get_model("authentik_stages_prompt", "PromptStage")
    Prompt = apps.get_model("authentik_stages_prompt", "Prompt")

    prompt_username, _ = Prompt.objects.using(db_alias).update_or_create(
        field_key="username",
        order=200,
        defaults={
            "label": "Username",
            "type": FieldTypes.TEXT,
            "placeholder": "return user.username",
            "placeholder_expression": True,
        },
    )
    prompt_name, _ = Prompt.objects.using(db_alias).update_or_create(
        field_key="name",
        order=201,
        defaults={
            "label": "Name",
            "type": FieldTypes.TEXT,
            "placeholder": "return user.name",
            "placeholder_expression": True,
        },
    )
    prompt_email, _ = Prompt.objects.using(db_alias).update_or_create(
        field_key="email",
        order=202,
        defaults={
            "label": "Email",
            "type": FieldTypes.EMAIL,
            "placeholder": "return user.email",
            "placeholder_expression": True,
        },
    )
    prompt_locale, _ = Prompt.objects.using(db_alias).update_or_create(
        field_key="locale",
        order=203,
        defaults={
            "label": "Locale",
            "type": FieldTypes.AK_LOCALE,
            "placeholder": 'return user.attributes.get("settings", {}).get("locale", "")',
            "placeholder_expression": True,
            "required": True,
        },
    )

    validation_policy, _ = ExpressionPolicy.objects.using(db_alias).update_or_create(
        name="default-user-settings-authorization",
        defaults={
            "expression": AUTHORIZATION_POLICY,
        },
    )
    prompt_stage, _ = PromptStage.objects.using(db_alias).update_or_create(
        name="default-user-settings",
    )
    prompt_stage.validation_policies.set([validation_policy])
    prompt_stage.fields.set([prompt_username, prompt_name, prompt_email, prompt_locale])
    prompt_stage.save()
    user_write, _ = UserWriteStage.objects.using(db_alias).update_or_create(
        name="default-user-settings-write"
    )

    flow, _ = Flow.objects.using(db_alias).update_or_create(
        slug="default-user-settings-flow",
        designation=FlowDesignation.STAGE_CONFIGURATION,
        defaults={
            "name": "Update your info",
        },
    )
    FlowStageBinding.objects.using(db_alias).update_or_create(
        target=flow,
        stage=prompt_stage,
        defaults={
            "order": 20,
        },
    )
    FlowStageBinding.objects.using(db_alias).update_or_create(
        target=flow,
        stage=user_write,
        defaults={
            "order": 100,
        },
    )

    tenant = Tenant.objects.using(db_alias).filter(default=True).first()
    if not tenant:
        return
    tenant.flow_user_settings = flow
    tenant.save()


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_policies_expression", "__latest__"),
        ("authentik_stages_prompt", "0007_prompt_placeholder_expression"),
        ("authentik_flows", "0021_auto_20211227_2103"),
        ("authentik_tenants", "0001_squashed_0005_tenant_web_certificate"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="flow_user_settings",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tenant_user_settings",
                to="authentik_flows.flow",
            ),
        ),
        migrations.RunPython(create_default_user_settings_flow),
    ]
