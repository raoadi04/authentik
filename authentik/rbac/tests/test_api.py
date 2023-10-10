"""RBAC role tests"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.utils.encoders import JSONEncoder

from authentik.core.models import Group
from authentik.core.tests.utils import create_test_admin_user, create_test_user
from authentik.lib.generators import generate_id
from authentik.rbac.models import Role
from authentik.stages.invitation.models import Invitation


class TestAPIPerms(APITestCase):
    """Test API Permission and filtering"""

    def setUp(self) -> None:
        self.superuser = create_test_admin_user()

        self.user = create_test_user()
        self.role = Role.objects.create(name=generate_id())
        self.group = Group.objects.create(name=generate_id())
        self.group.roles.add(self.role)
        self.group.users.add(self.user)

    def test_list_simple(self):
        """Test list (single object, role has global permission)"""
        self.client.force_login(self.user)
        self.role.assign_permission("authentik_stages_invitation.view_invitation")

        Invitation.objects.all().delete()
        inv = Invitation.objects.create(
            name=generate_id(),
            created_by=self.superuser,
        )
        res = self.client.get(reverse("authentik_api:invitation-list"))
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(
            res.content.decode(),
            {
                "pagination": {
                    "next": 0,
                    "previous": 0,
                    "count": 1,
                    "current": 1,
                    "total_pages": 1,
                    "start_index": 1,
                    "end_index": 1,
                },
                "results": [
                    {
                        "pk": str(inv.pk),
                        "name": inv.name,
                        "expires": JSONEncoder().default(inv.expires),
                        "fixed_data": {},
                        "created_by": {
                            "pk": self.superuser.pk,
                            "username": f"{self.superuser.username}",
                            "name": f"{self.superuser.username}",
                            "is_active": True,
                            "last_login": None,
                            "email": f"{self.superuser.username}@goauthentik.io",
                            "attributes": {},
                            "uid": self.superuser.uid,
                        },
                        "single_use": False,
                        "flow": None,
                        "flow_obj": None,
                    }
                ],
            },
        )

    def test_list_object_perm(self):
        """Test list"""
        self.client.force_login(self.user)

        Invitation.objects.all().delete()
        Invitation.objects.create(
            name=generate_id(),
            created_by=self.superuser,
        )
        inv2 = Invitation.objects.create(
            name=generate_id(),
            created_by=self.superuser,
        )
        self.role.assign_permission("authentik_stages_invitation.view_invitation", obj=inv2)

        res = self.client.get(reverse("authentik_api:invitation-list"))
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(
            res.content.decode(),
            {
                "pagination": {
                    "next": 0,
                    "previous": 0,
                    "count": 1,
                    "current": 1,
                    "total_pages": 1,
                    "start_index": 1,
                    "end_index": 1,
                },
                "results": [
                    {
                        "pk": str(inv2.pk),
                        "name": inv2.name,
                        "expires": JSONEncoder().default(inv2.expires),
                        "fixed_data": {},
                        "created_by": {
                            "pk": self.superuser.pk,
                            "username": f"{self.superuser.username}",
                            "name": f"{self.superuser.username}",
                            "is_active": True,
                            "last_login": None,
                            "email": f"{self.superuser.username}@goauthentik.io",
                            "attributes": {},
                            "uid": self.superuser.uid,
                        },
                        "single_use": False,
                        "flow": None,
                        "flow_obj": None,
                    }
                ],
            },
        )

    def test_list_denied(self):
        """Test list without adding permission"""
        self.client.force_login(self.user)

        res = self.client.get(reverse("authentik_api:invitation-list"))
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(
            res.content.decode(),
            {
                "pagination": {
                    "count": 0,
                    "current": 1,
                    "end_index": 0,
                    "next": 0,
                    "previous": 0,
                    "start_index": 0,
                    "total_pages": 1,
                },
                "results": [],
            },
        )

    def test_create_simple(self):
        """Test create with permission"""
        self.client.force_login(self.user)
        self.role.assign_permission("authentik_stages_invitation.add_invitation")
        res = self.client.post(
            reverse("authentik_api:invitation-list"),
            data={
                "name": generate_id(),
            },
        )
        self.assertEqual(res.status_code, 201)

    def test_create_simple_denied(self):
        """Test create without assigning permission"""
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("authentik_api:invitation-list"),
            data={
                "name": generate_id(),
            },
        )
        self.assertEqual(res.status_code, 403)
