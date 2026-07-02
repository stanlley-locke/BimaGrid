"""RBAC permissions and queryset scoping tests."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Profile
from apps.core.permissions import IsAdminUser, IsBrokerOrAdmin, IsFarmerOrAbove
from apps.core.queryset import (
	is_admin,
	is_broker,
	scope_onboarding_queryset,
	scope_policy_queryset,
	scope_profile_queryset,
	user_role,
)
from apps.onboarding.models import FarmerOnboarding
from apps.policies.models import Policy
from tests.factories import PolicyFactory, ProfileFactory

User = get_user_model()


class MockRequest:
	def __init__(self, user, method="GET"):
		self.user = user
		self.method = method


class PermissionsTests(TestCase):
	def test_admin_user_permission(self):
		user = User.objects.create_user(username="adm", email="a@x.com", password="x")
		Profile.objects.create(user=user, full_name="Admin", role=Profile.Role.ADMIN)
		self.assertTrue(IsAdminUser().has_permission(MockRequest(user), None))

	def test_broker_has_broker_or_admin(self):
		user = User.objects.create_user(username="brk", email="b@x.com", password="x")
		Profile.objects.create(user=user, full_name="Broker", role=Profile.Role.BROKER)
		self.assertTrue(IsBrokerOrAdmin().has_permission(MockRequest(user), None))

	def test_farmer_cannot_access_admin_only(self):
		user = User.objects.create_user(username="frm", email="f@x.com", password="x")
		Profile.objects.create(user=user, full_name="Farmer", role=Profile.Role.FARMER)
		self.assertFalse(IsAdminUser().has_permission(MockRequest(user), None))
		self.assertTrue(IsFarmerOrAbove().has_permission(MockRequest(user), None))


class QuerysetScopingTests(TestCase):
	def setUp(self):
		self.broker_profile = ProfileFactory(role=Profile.Role.BROKER)
		self.farmer_a = ProfileFactory(role=Profile.Role.FARMER)
		self.farmer_b = ProfileFactory(role=Profile.Role.FARMER)
		self.onboarding_a = self.farmer_a.onboarding
		self.onboarding_a.assigned_agent = self.broker_profile
		self.onboarding_a.save(update_fields=["assigned_agent", "updated_at"])
		self.onboarding_b = self.farmer_b.onboarding
		PolicyFactory(onboarding=self.onboarding_a, policy_number="POL-A")
		PolicyFactory(onboarding=self.onboarding_b, policy_number="POL-B")

	def test_admin_sees_all_policies(self):
		admin = User.objects.create_user(username="admin2", is_staff=True, password="x")
		Profile.objects.create(user=admin, full_name="Staff", role=Profile.Role.ADMIN)
		qs = scope_policy_queryset(Policy.objects.all(), admin)
		self.assertEqual(qs.count(), 2)

	def test_broker_sees_assigned_policies_only(self):
		qs = scope_policy_queryset(Policy.objects.all(), self.broker_profile.user)
		self.assertEqual(qs.count(), 1)
		self.assertEqual(qs.first().policy_number, "POL-A")

	def test_farmer_sees_own_policies_only(self):
		qs = scope_policy_queryset(Policy.objects.all(), self.farmer_a.user)
		self.assertEqual(qs.count(), 1)
		self.assertEqual(qs.first().policy_number, "POL-A")

	def test_user_role_helpers(self):
		self.assertTrue(is_admin(User.objects.create_user(username="s", is_staff=True, password="x")))
		self.assertTrue(is_broker(self.broker_profile.user))
		self.assertEqual(user_role(self.farmer_a.user), Profile.Role.FARMER)

	def test_scope_onboarding_for_broker(self):
		qs = scope_onboarding_queryset(FarmerOnboarding.objects.all(), self.broker_profile.user)
		self.assertEqual(qs.count(), 1)

	def test_scope_profile_for_broker_includes_self(self):
		qs = scope_profile_queryset(Profile.objects.all(), self.broker_profile.user)
		self.assertIn(self.broker_profile, qs)
