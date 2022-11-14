# Generated by Django 4.1.3 on 2022-11-14 09:23
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def migrate_hibp_policy(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    db_alias = schema_editor.connection.alias

    HaveIBeenPwendPolicy = apps.get_model("authentik_policies_hibp", "HaveIBeenPwendPolicy")
    PasswordPolicy = apps.get_model("authentik_policies_password", "PasswordPolicy")

    PolicyBinding = apps.get_model("authentik_policies", "PolicyBinding")

    for old_policy in HaveIBeenPwendPolicy.objects.using(db_alias).all():
        new_policy = PasswordPolicy.objects.using(db_alias).create(
            name=old_policy.name,
            hibp_allowed_count=old_policy.allowed_count,
            password_field=old_policy.password_field,
            execution_logging=old_policy.execution_logging,
            check_static_rules=False,
            check_have_i_been_pwned=True,
        )
        PolicyBinding.objects.using(db_alias).filter(policy=old_policy).update(policy=new_policy)
        old_policy.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_policies_hibp", "0003_haveibeenpwendpolicy_authentik_p_policy__6957d7_idx"),
        ("authentik_policies_password", "0004_passwordpolicy_authentik_p_policy__855e80_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="passwordpolicy",
            name="check_have_i_been_pwned",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="passwordpolicy",
            name="check_static_rules",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="passwordpolicy",
            name="check_zxcvbn",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="passwordpolicy",
            name="hibp_allowed_count",
            field=models.PositiveIntegerField(
                default=0,
                help_text="How many times the password hash is allowed to be on haveibeenpwned",
            ),
        ),
        migrations.AddField(
            model_name="passwordpolicy",
            name="zxcvbn_score_threshold",
            field=models.PositiveIntegerField(
                default=2,
                help_text="If the zxcvbn score is equal or less than this value, the policy will fail.",
            ),
        ),
        migrations.AlterField(
            model_name="passwordpolicy",
            name="error_message",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(migrate_hibp_policy),
    ]
