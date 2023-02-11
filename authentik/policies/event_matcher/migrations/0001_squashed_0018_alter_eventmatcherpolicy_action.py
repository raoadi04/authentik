# Generated by Django 3.2.8 on 2021-10-10 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ("authentik_policies_event_matcher", "0001_initial"),
        ("authentik_policies_event_matcher", "0002_auto_20201230_2046"),
        ("authentik_policies_event_matcher", "0003_auto_20210110_1907"),
        ("authentik_policies_event_matcher", "0004_auto_20210112_2158"),
        ("authentik_policies_event_matcher", "0005_auto_20210202_1821"),
        ("authentik_policies_event_matcher", "0006_auto_20210203_1134"),
        ("authentik_policies_event_matcher", "0007_auto_20210209_1657"),
        ("authentik_policies_event_matcher", "0008_auto_20210213_1640"),
        ("authentik_policies_event_matcher", "0009_auto_20210215_2159"),
        ("authentik_policies_event_matcher", "0010_auto_20210222_1821"),
        ("authentik_policies_event_matcher", "0011_auto_20210302_0856"),
        ("authentik_policies_event_matcher", "0012_auto_20210323_1339"),
        ("authentik_policies_event_matcher", "0013_alter_eventmatcherpolicy_app"),
        ("authentik_policies_event_matcher", "0014_alter_eventmatcherpolicy_app"),
        ("authentik_policies_event_matcher", "0015_alter_eventmatcherpolicy_app"),
        ("authentik_policies_event_matcher", "0016_alter_eventmatcherpolicy_action"),
        ("authentik_policies_event_matcher", "0017_alter_eventmatcherpolicy_action"),
        ("authentik_policies_event_matcher", "0018_alter_eventmatcherpolicy_action"),
    ]

    initial = True

    dependencies = [
        ("authentik_policies", "0004_policy_execution_logging"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventMatcherPolicy",
            fields=[
                (
                    "policy_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="authentik_policies.policy",
                    ),
                ),
                (
                    "action",
                    models.TextField(
                        blank=True,
                        choices=[
                            ("login", "Login"),
                            ("login_failed", "Login Failed"),
                            ("logout", "Logout"),
                            ("user_write", "User Write"),
                            ("suspicious_request", "Suspicious Request"),
                            ("password_set", "Password Set"),
                            ("secret_view", "Secret View"),
                            ("secret_rotate", "Secret Rotate"),
                            ("invitation_used", "Invite Used"),
                            ("authorize_application", "Authorize Application"),
                            ("source_linked", "Source Linked"),
                            ("impersonation_started", "Impersonation Started"),
                            ("impersonation_ended", "Impersonation Ended"),
                            ("flow_execution", "Flow Execution"),
                            ("policy_execution", "Policy Execution"),
                            ("policy_exception", "Policy Exception"),
                            ("property_mapping_exception", "Property Mapping Exception"),
                            ("system_task_execution", "System Task Execution"),
                            ("system_task_exception", "System Task Exception"),
                            ("system_exception", "System Exception"),
                            ("configuration_error", "Configuration Error"),
                            ("model_created", "Model Created"),
                            ("model_updated", "Model Updated"),
                            ("model_deleted", "Model Deleted"),
                            ("email_sent", "Email Sent"),
                            ("update_available", "Update Available"),
                            ("custom_", "Custom Prefix"),
                        ],
                        help_text=(
                            "Match created events with this action type. When left empty, all"
                            " action types will be matched."
                        ),
                    ),
                ),
                (
                    "client_ip",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Matches Event's Client IP (strict matching, for network matching use"
                            " an Expression Policy)"
                        ),
                    ),
                ),
                (
                    "app",
                    models.TextField(
                        blank=True,
                        choices=[
                            ("authentik.admin", "authentik Admin"),
                            ("authentik.api", "authentik API"),
                            ("authentik.events", "authentik Events"),
                            ("authentik.crypto", "authentik Crypto"),
                            ("authentik.flows", "authentik Flows"),
                            ("authentik.outposts", "authentik Outpost"),
                            ("authentik.lib", "authentik lib"),
                            ("authentik.policies", "authentik Policies"),
                            ("authentik.policies.dummy", "authentik Policies.Dummy"),
                            (
                                "authentik.policies.event_matcher",
                                "authentik Policies.Event Matcher",
                            ),
                            ("authentik.policies.expiry", "authentik Policies.Expiry"),
                            ("authentik.policies.expression", "authentik Policies.Expression"),
                            ("authentik.policies.hibp", "authentik Policies.HaveIBeenPwned"),
                            ("authentik.policies.password", "authentik Policies.Password"),
                            ("authentik.policies.reputation", "authentik Policies.Reputation"),
                            ("authentik.providers.proxy", "authentik Providers.Proxy"),
                            ("authentik.providers.ldap", "authentik Providers.LDAP"),
                            ("authentik.providers.oauth2", "authentik Providers.OAuth2"),
                            ("authentik.providers.saml", "authentik Providers.SAML"),
                            ("authentik.recovery", "authentik Recovery"),
                            ("authentik.sources.ldap", "authentik Sources.LDAP"),
                            ("authentik.sources.oauth", "authentik Sources.OAuth"),
                            ("authentik.sources.plex", "authentik Sources.Plex"),
                            ("authentik.sources.saml", "authentik Sources.SAML"),
                            (
                                "authentik.stages.authenticator_duo",
                                "authentik Stages.Authenticator.Duo",
                            ),
                            (
                                "authentik.stages.authenticator_static",
                                "authentik Stages.Authenticator.Static",
                            ),
                            (
                                "authentik.stages.authenticator_totp",
                                "authentik Stages.Authenticator.TOTP",
                            ),
                            (
                                "authentik.stages.authenticator_validate",
                                "authentik Stages.Authenticator.Validate",
                            ),
                            (
                                "authentik.stages.authenticator_webauthn",
                                "authentik Stages.Authenticator.WebAuthn",
                            ),
                            ("authentik.stages.captcha", "authentik Stages.Captcha"),
                            ("authentik.stages.consent", "authentik Stages.Consent"),
                            ("authentik.stages.deny", "authentik Stages.Deny"),
                            ("authentik.stages.dummy", "authentik Stages.Dummy"),
                            ("authentik.stages.email", "authentik Stages.Email"),
                            ("authentik.stages.identification", "authentik Stages.Identification"),
                            ("authentik.stages.invitation", "authentik Stages.User Invitation"),
                            ("authentik.stages.password", "authentik Stages.Password"),
                            ("authentik.stages.prompt", "authentik Stages.Prompt"),
                            ("authentik.stages.user_delete", "authentik Stages.User Delete"),
                            ("authentik.stages.user_login", "authentik Stages.User Login"),
                            ("authentik.stages.user_logout", "authentik Stages.User Logout"),
                            ("authentik.stages.user_write", "authentik Stages.User Write"),
                            ("authentik.tenants", "authentik Tenants"),
                            ("authentik.core", "authentik Core"),
                            ("authentik.blueprints", "authentik Blueprints"),
                        ],
                        default="",
                        help_text=(
                            "Match events created by selected application. When left empty, all"
                            " applications are matched."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Event Matcher Policy",
                "verbose_name_plural": "Event Matcher Policies",
            },
            bases=("authentik_policies.policy",),
        ),
    ]
