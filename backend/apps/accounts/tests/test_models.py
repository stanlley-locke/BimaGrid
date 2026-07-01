from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Profile
from apps.accounts.services import get_or_create_profile


User = get_user_model()


class ProfileModelTests(TestCase):
	def test_profile_string_uses_full_name(self):
		user = User.objects.create_user(username="jane", email="jane@example.com", password="strong-pass-123")
		profile = Profile.objects.create(user=user, full_name="Jane Doe")

		self.assertEqual(str(profile), "Jane Doe")

	def test_service_creates_missing_profile(self):
		user = User.objects.create_user(username="john", email="john@example.com", password="strong-pass-123")

		profile = get_or_create_profile(user)

		self.assertEqual(profile.user, user)
		self.assertTrue(Profile.objects.filter(user=user).exists())
