from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Profile


User = get_user_model()


class OnboardingViewTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_onboarding_requires_authentication(self):
		response = self.client.get("/api/onboarding/")

		self.assertEqual(response.status_code, 401)

	def test_current_onboarding_returns_created_workflow(self):
		user = User.objects.create_user(username="viewer", email="viewer@example.com", password="strong-pass-123")
		Profile.objects.create(user=user, full_name="Viewer Farmer")
		self.client.force_authenticate(user=user)

		response = self.client.get("/api/onboarding/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["status"], "draft")

	def test_submit_onboarding_marks_workflow_submitted(self):
		user = User.objects.create_user(username="submitter", email="submitter@example.com", password="strong-pass-123")
		Profile.objects.create(user=user, full_name="Submitter Farmer")
		self.client.force_authenticate(user=user)

		response = self.client.post(
			"/api/onboarding/submit/",
			{
				"ward_code": "WARD-002",
				"crop": "maize",
				"acreage": "1.75",
				"mpesa_number": "254712345678",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["status"], "submitted")