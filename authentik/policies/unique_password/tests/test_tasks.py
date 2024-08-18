from datetime import datetime, timedelta

from django.test import TestCase

from authentik.core.models import User
from authentik.core.tests.utils import create_test_user
from authentik.policies.models import PolicyBinding, PolicyBindingModel
from authentik.policies.unique_password.models import UniquePasswordPolicy, UserPasswordHistory
from authentik.policies.unique_password.tasks import (
    purge_password_history_table,
    trim_user_password_history,
)


class TestPurgePasswordHistory(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(username="testuser")

    def test_purge_password_history_table(self):
        """Tests the task empties the UserPasswordHistory table"""
        UserPasswordHistory.objects.bulk_create(
            [
                UserPasswordHistory(user=self.user, old_password="hunter1"),
                UserPasswordHistory(user=self.user, old_password="hunter2"),
            ]
        )
        purge_password_history_table.delay().get()
        self.assertFalse(UserPasswordHistory.objects.all())


class TestTrimPasswordHistory(TestCase):
    """Test password history cleanup task"""

    def setUp(self):
        self.user = create_test_user("test-user")
        self.pbm = PolicyBindingModel.objects.create()

    def test_trim_password_history_ok(self):
        """Test passwors over the define limit are deleted"""
        _now = datetime.now()
        UserPasswordHistory.objects.bulk_create(
            [
                UserPasswordHistory(
                    user=self.user,
                    old_password="hunter1",
                    created_at=_now - timedelta(days=3),
                ),
                UserPasswordHistory(
                    user=self.user,
                    old_password="hunter2",
                    created_at=_now - timedelta(days=2),
                ),
                UserPasswordHistory(user=self.user, old_password="hunter3", created_at=_now),
            ]
        )

        policy = UniquePasswordPolicy.objects.create(num_historical_passwords=1)
        PolicyBinding.objects.create(
            target=self.pbm,
            policy=policy,
            enabled=True,
            order=0,
        )
        trim_user_password_history(self.user.pk)
        user_pwd_history_qs = UserPasswordHistory.objects.filter(user=self.user)
        self.assertEqual(len(user_pwd_history_qs), 1)

    def test_trim_password_history_policy_diabled_no_op(self):
        """Test no passwords removed if policy binding is disabled"""

        # Insert a record to ensure it's not deleted after executing task
        UserPasswordHistory.objects.create(user=self.user, old_password="hunter2")

        policy = UniquePasswordPolicy.objects.create(num_historical_passwords=1)
        PolicyBinding.objects.create(
            target=self.pbm,
            policy=policy,
            enabled=False,
            order=0,
        )
        trim_user_password_history(self.user.pk)
        self.assertTrue(UserPasswordHistory.objects.filter(user=self.user))

    def test_trim_password_history_fewer_records_than_maximum_is_no_op(self):
        """Test no passwords deleted if fewer passwords exist than limit"""

        UserPasswordHistory.objects.create(user=self.user, old_password="hunter2")

        policy = UniquePasswordPolicy.objects.create(num_historical_passwords=2)
        PolicyBinding.objects.create(
            target=self.pbm,
            policy=policy,
            enabled=True,
            order=0,
        )
        trim_user_password_history(self.user.pk)
        self.assertTrue(UserPasswordHistory.objects.filter(user=self.user).exists())
