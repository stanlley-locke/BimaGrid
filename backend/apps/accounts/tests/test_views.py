from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from tests.utils import create_admin_user, create_user_with_profile, token_client


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

	def test_login_returns_bearer_token(self):
		User.objects.create_user(
			username="loginuser",
			email="loginuser@example.com",
			password="strong-pass-123",
		)
		response = self.client.post(
			"/api/accounts/login/",
			{"username": "loginuser", "password": "strong-pass-123"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn("token", response.data)
		self.assertEqual(response.data["user"]["username"], "loginuser")

	def test_login_accepts_email_identifier(self):
		User.objects.create_user(
			username="emailuser",
			email="emailuser@example.com",
			password="strong-pass-123",
		)
		response = self.client.post(
			"/api/accounts/login/",
			{"username": "emailuser@example.com", "password": "strong-pass-123"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn("token", response.data)

	def test_login_rejects_invalid_credentials(self):
		User.objects.create_user(
			username="badlogin",
			email="badlogin@example.com",
			password="strong-pass-123",
		)
		response = self.client.post(
			"/api/accounts/login/",
			{"username": "badlogin", "password": "wrong-password"},
			format="json",
		)

		self.assertEqual(response.status_code, 400)

	def test_me_accepts_bearer_token(self):
		user = User.objects.create_user(
			username="beareruser",
			email="beareruser@example.com",
			password="strong-pass-123",
		)
		Profile.objects.create(user=user, full_name="Bearer User")
		login_response = self.client.post(
			"/api/accounts/login/",
			{"username": "beareruser", "password": "strong-pass-123"},
			format="json",
		)
		token = login_response.data["token"]

		response = self.client.get(
			"/api/accounts/me/",
			HTTP_AUTHORIZATION=f"Bearer {token}",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["username"], "beareruser")

	def test_me_endpoint_requires_authentication(self):
		response = self.client.get("/api/accounts/me/")

		self.assertIn(response.status_code, [401, 403])

	def test_me_endpoint_returns_profile_for_authenticated_user(self):
		user = User.objects.create_user(username="viewer", email="viewer@example.com", password="strong-pass-123")
		Profile.objects.create(user=user, full_name="Viewer User")
		self.client.force_authenticate(user=user)

		response = self.client.get("/api/accounts/me/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["username"], "viewer")

	def test_admin_can_access_me_with_token(self):
		admin, _ = create_admin_user("staff_admin")
		client = token_client(admin)
		response = client.get("/api/accounts/me/")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["profile"]["role"], Profile.Role.ADMIN)

	def test_create_user_with_profile_helper(self):
		user, profile, onboarding = create_user_with_profile(
			"helper_user",
			full_name="Helper User",
			role=Profile.Role.FARMER,
		)
		self.assertEqual(profile.full_name, "Helper User")
		self.assertEqual(onboarding.profile, profile)
