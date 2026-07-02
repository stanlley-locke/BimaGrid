"""Admin dashboard God Mode tests."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from apps.accounts.models import Profile
from apps.policies.models import Policy
from tests.utils import create_admin_user, create_policy_for_profile, token_client

User = get_user_model()


class GodModeDashboardTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_dashboard_requires_admin(self):
		user = User.objects.create_user(username="farmer", email="f@example.com", password="test-pass-123")
		Profile.objects.create(user=user, full_name="Farmer", role=Profile.Role.FARMER)
		self.client.force_login(user)
		response = self.client.get("/api/admin/")
		self.assertEqual(response.status_code, 403)

	def test_dashboard_renders_for_admin(self):
		admin, _ = create_admin_user()
		self.client.force_login(admin)
		response = self.client.get("/api/admin/")
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "BimaGrid God Mode")


class GodModeApiTests(TestCase):
	def test_simulate_drought_requires_admin(self):
		user = User.objects.create_user(username="user1", email="u1@example.com", password="test-pass-123")
		Profile.objects.create(user=user, full_name="User")
		client = token_client(user)
		response = client.post(
			"/api/admin/simulate-drought/",
			{"h3_index": "8928308280fffff", "rainfall_mm": 10, "ndvi": 0.3},
			format="json",
		)
		self.assertEqual(response.status_code, 403)

	def test_simulate_drought_succeeds_for_admin(self):
		admin, _ = create_admin_user()
		client = token_client(admin)
		response = client.post(
			"/api/admin/simulate-drought/",
			{"h3_index": "8928308280fffff", "rainfall_mm": 10, "ndvi": 0.3},
			format="json",
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["h3_index"], "8928308280fffff")

	def test_bypass_payment_activates_policy(self):
		admin, _ = create_admin_user()
		user = User.objects.create_user(username="payuser", email="pay@example.com", password="test-pass-123")
		profile = Profile.objects.create(user=user, full_name="Pay User", phone_number="254700000099")
		policy = create_policy_for_profile(profile, policy_number="POL-BYPASS-001")
		client = token_client(admin)
		response = client.post(
			"/api/admin/bypass-payment/",
			{"policy_id": policy.policy_number},
			format="json",
		)
		self.assertEqual(response.status_code, 200)
		policy.refresh_from_db()
		self.assertEqual(policy.status, Policy.Status.ACTIVE)

	def test_trigger_evaluation_queues_task(self):
		admin, _ = create_admin_user()
		client = token_client(admin)
		response = client.post(
			"/api/admin/trigger-evaluation/",
			{"h3_index": "8928308280fffff"},
			format="json",
		)
		self.assertEqual(response.status_code, 202)
		self.assertIn("task_id", response.data)
