from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Profile


User = get_user_model()


class AccountsViewTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_registration_endpoint_creates_account(self):
		response = self.client.post(
			"/api/accounts/register/",
			{
				"username": "newuser",
				"email": "newuser@example.com",
				"password": "strong-pass-123",
				"full_name": "New User",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertTrue(User.objects.filter(username="newuser").exists())

	def test_me_endpoint_requires_authentication(self):
		response = self.client.get("/api/accounts/me/")

		self.assertEqual(response.status_code, 401)

	def test_me_endpoint_returns_profile_for_authenticated_user(self):
		user = User.objects.create_user(username="viewer", email="viewer@example.com", password="strong-pass-123")
		Profile.objects.create(user=user, full_name="Viewer User")
		self.client.force_authenticate(user=user)

		response = self.client.get("/api/accounts/me/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["username"], "viewer")
