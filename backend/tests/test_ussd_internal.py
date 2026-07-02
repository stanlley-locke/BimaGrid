"""USSD internal API integration tests."""

from django.test import Client, TestCase, override_settings

from apps.accounts.models import Profile
from apps.policies.models import Policy
from tests.utils import create_policy_for_profile


@override_settings(USSD_INTERNAL_API_KEY="test-internal-key", DEBUG=False)
class UssdInternalApiTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.headers = {"HTTP_X_USSD_INTERNAL_KEY": "test-internal-key"}

	def test_register_creates_onboarding(self):
		response = self.client.post(
			"/api/v1/ussd/internal/register/",
			{
				"phone": "254711122233",
				"ward_code": "5678",
				"crop": "maize",
				"acreage": "3.0",
				"mpesa_number": "254711122233",
			},
			content_type="application/json",
			**self.headers,
		)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.json()["status"], "submitted")
		self.assertTrue(Profile.objects.filter(phone_number="254711122233").exists())

	def test_policy_status_not_found(self):
		response = self.client.get(
			"/api/v1/ussd/internal/policy-status/",
			{"phone": "254799988877"},
			**self.headers,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["status"], "not_found")

	def test_policy_status_returns_policy(self):
		from django.contrib.auth import get_user_model

		User = get_user_model()
		user = User.objects.create_user(username="ussd_farmer", email="ussd@x.com", password="x")
		profile = Profile.objects.create(
			user=user,
			full_name="USSD Farmer",
			phone_number="254733344455",
			role=Profile.Role.FARMER,
		)
		policy = create_policy_for_profile(profile, policy_number="POL-USSD-001")

		response = self.client.get(
			"/api/v1/ussd/internal/policy-status/",
			{"phone": "254733344455"},
			**self.headers,
		)
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(data["status"], "ok")
		self.assertEqual(data["policy_number"], policy.policy_number)

	def test_claim_returns_automatic_message(self):
		from django.contrib.auth import get_user_model

		User = get_user_model()
		user = User.objects.create_user(username="claim_user", email="c@x.com", password="x")
		profile = Profile.objects.create(
			user=user,
			full_name="Claim Farmer",
			phone_number="254744455566",
			role=Profile.Role.FARMER,
		)
		create_policy_for_profile(profile, policy_number="POL-CLAIM-001", status=Policy.Status.ACTIVE)

		response = self.client.post(
			"/api/v1/ussd/internal/claim/",
			{"phone": "254744455566", "loss_type": "drought"},
			content_type="application/json",
			**self.headers,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["status"], "automatic")
