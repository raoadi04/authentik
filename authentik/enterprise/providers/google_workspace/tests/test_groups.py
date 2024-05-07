"""Google Workspace Group tests"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from authentik.blueprints.tests import apply_blueprint
from authentik.core.models import Application, Group, User
from authentik.core.tests.utils import create_test_user
from authentik.enterprise.providers.google_workspace.clients.test_http import MockHTTP
from authentik.enterprise.providers.google_workspace.models import (
    GoogleWorkspaceDeleteAction,
    GoogleWorkspaceProvider,
    GoogleWorkspaceProviderGroup,
    GoogleWorkspaceProviderMapping,
)
from authentik.enterprise.providers.google_workspace.tasks import google_workspace_sync
from authentik.events.models import Event, EventAction
from authentik.lib.generators import generate_id
from authentik.lib.tests.utils import load_fixture
from authentik.tenants.models import Tenant

domains_list_v1_mock = load_fixture("fixtures/domains_list_v1.json")


class GoogleWorkspaceGroupTests(TestCase):
    """Google workspace Group tests"""

    @apply_blueprint("system/providers-google-workspace.yaml")
    def setUp(self) -> None:
        # Delete all groups and groups as the mocked HTTP responses only return one ID
        # which will cause errors with multiple groups
        Tenant.objects.update(avatars="none")
        User.objects.all().exclude_anonymous().delete()
        Group.objects.all().delete()
        self.provider: GoogleWorkspaceProvider = GoogleWorkspaceProvider.objects.create(
            name=generate_id(),
            credentials={},
            delegated_subject="",
            exclude_users_service_account=True,
        )
        self.app: Application = Application.objects.create(
            name=generate_id(),
            slug=generate_id(),
        )
        self.app.backchannel_providers.add(self.provider)
        self.provider.property_mappings.add(
            GoogleWorkspaceProviderMapping.objects.get(
                managed="goauthentik.io/providers/google_workspace/user"
            )
        )
        self.provider.property_mappings_group.add(
            GoogleWorkspaceProviderMapping.objects.get(
                managed="goauthentik.io/providers/google_workspace/group"
            )
        )
        self.api_key = generate_id()

    def test_group_create(self):
        """Test group creation"""
        uid = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?key={self.api_key}&alt=json",
            method="POST",
            body={"id": generate_id()},
        )
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            group = Group.objects.create(name=uid)
            google_group = GoogleWorkspaceProviderGroup.objects.filter(
                provider=self.provider, group=group
            ).first()
            self.assertIsNotNone(google_group)
            self.assertFalse(Event.objects.filter(action=EventAction.SYSTEM_EXCEPTION).exists())
            self.assertEqual(len(http.requests()), 2)

    def test_group_create_update(self):
        """Test group updating"""
        uid = generate_id()
        ext_id = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?key={self.api_key}&alt=json",
            method="POST",
            body={"id": ext_id},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups/{ext_id}?key={self.api_key}&alt=json",
            method="PUT",
            body={"id": ext_id},
        )
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            group = Group.objects.create(name=uid)
            google_group = GoogleWorkspaceProviderGroup.objects.filter(
                provider=self.provider, group=group
            ).first()
            self.assertIsNotNone(google_group)

            group.name = "new name"
            group.save()
            self.assertFalse(Event.objects.filter(action=EventAction.SYSTEM_EXCEPTION).exists())
            self.assertEqual(len(http.requests()), 4)

    def test_group_create_delete(self):
        """Test group deletion"""
        uid = generate_id()
        ext_id = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?key={self.api_key}&alt=json",
            method="POST",
            body={"id": ext_id},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups/{ext_id}?key={self.api_key}",
            method="DELETE",
        )
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            group = Group.objects.create(name=uid)
            google_group = GoogleWorkspaceProviderGroup.objects.filter(
                provider=self.provider, group=group
            ).first()
            self.assertIsNotNone(google_group)

            group.delete()
            self.assertFalse(Event.objects.filter(action=EventAction.SYSTEM_EXCEPTION).exists())
            self.assertEqual(len(http.requests()), 4)

    def test_group_create_member_add(self):
        """Test group creation"""
        uid = generate_id()
        ext_id = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?key={self.api_key}&alt=json",
            method="POST",
            body={"id": ext_id},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/users?key={self.api_key}&alt=json",
            method="POST",
            body={"primaryEmail": f"{uid}@goauthentik.io"},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/users/{uid}%40goauthentik.io?key={self.api_key}&alt=json",
            method="PUT",
            body={"primaryEmail": f"{uid}@goauthentik.io"},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups/{ext_id}/members?key={self.api_key}&alt=json",
            method="POST",
        )
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            user = create_test_user(uid)
            group = Group.objects.create(name=uid)
            group.users.add(user)
            google_group = GoogleWorkspaceProviderGroup.objects.filter(
                provider=self.provider, group=group
            ).first()
            self.assertIsNotNone(google_group)
            self.assertFalse(Event.objects.filter(action=EventAction.SYSTEM_EXCEPTION).exists())
            self.assertEqual(len(http.requests()), 8)

    def test_group_create_member_remove(self):
        """Test group creation"""
        uid = generate_id()
        ext_id = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?key={self.api_key}&alt=json",
            method="POST",
            body={"id": ext_id},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/users?key={self.api_key}&alt=json",
            method="POST",
            body={"primaryEmail": f"{uid}@goauthentik.io"},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/users/{uid}%40goauthentik.io?key={self.api_key}&alt=json",
            method="PUT",
            body={"primaryEmail": f"{uid}@goauthentik.io"},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups/{ext_id}/members/{uid}%40goauthentik.io?key={self.api_key}",
            method="DELETE",
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups/{ext_id}/members?key={self.api_key}&alt=json",
            method="POST",
        )
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            user = create_test_user(uid)
            group = Group.objects.create(name=uid)
            group.users.add(user)
            google_group = GoogleWorkspaceProviderGroup.objects.filter(
                provider=self.provider, group=group
            ).first()
            self.assertIsNotNone(google_group)
            group.users.remove(user)

            self.assertFalse(Event.objects.filter(action=EventAction.SYSTEM_EXCEPTION).exists())
            self.assertEqual(len(http.requests()), 10)

    def test_group_create_delete_do_nothing(self):
        """Test group deletion (delete action = do nothing)"""
        self.provider.group_delete_action = GoogleWorkspaceDeleteAction.DO_NOTHING
        self.provider.save()
        uid = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?key={self.api_key}&alt=json",
            method="POST",
            body={"id": uid},
        )
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            group = Group.objects.create(name=uid)
            google_group = GoogleWorkspaceProviderGroup.objects.filter(
                provider=self.provider, group=group
            ).first()
            self.assertIsNotNone(google_group)

            group.delete()
            self.assertEqual(len(http.requests()), 3)
            self.assertFalse(
                GoogleWorkspaceProviderGroup.objects.filter(
                    provider=self.provider, group__name=uid
                ).exists()
            )

    def test_sync_task(self):
        """Test group discovery"""
        uid = generate_id()
        http = MockHTTP()
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/customer/my_customer/domains?key={self.api_key}&alt=json",
            domains_list_v1_mock,
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/users?customer=my_customer&maxResults=500&orderBy=email&key={self.api_key}&alt=json",
            method="GET",
            body={"users": []},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups?customer=my_customer&maxResults=500&orderBy=email&key={self.api_key}&alt=json",
            method="GET",
            body={"groups": [{"id": uid, "name": uid}]},
        )
        http.add_response(
            f"https://admin.googleapis.com/admin/directory/v1/groups/{uid}?key={self.api_key}&alt=json",
            method="PUT",
            body={"id": uid},
        )
        self.app.backchannel_providers.remove(self.provider)
        different_group = Group.objects.create(
            name=uid,
        )
        self.app.backchannel_providers.add(self.provider)
        with patch(
            "authentik.enterprise.providers.google_workspace.models.GoogleWorkspaceProvider.google_credentials",
            MagicMock(return_value={"developerKey": self.api_key, "http": http}),
        ):
            google_workspace_sync.delay(self.provider.pk).get()
            self.assertTrue(
                GoogleWorkspaceProviderGroup.objects.filter(
                    group=different_group, provider=self.provider
                ).exists()
            )
            self.assertFalse(Event.objects.filter(action=EventAction.SYSTEM_EXCEPTION).exists())
            self.assertEqual(len(http.requests()), 5)
