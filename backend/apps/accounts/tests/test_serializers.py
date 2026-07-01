from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Profile
from apps.accounts.serializers import AccountSerializer, RegistrationSerializer


User = get_user_model()


class RegistrationSerializerTests(TestCase):
	def test_registration_serializer_creates_user_and_profile(self):
		serializer = RegistrationSerializer(
			data={
				"username": "farmer1",
				"email": "farmer@example.com",
				"password": "strong-pass-123",
				"full_name": "Farmer One",
				"phone_number": "+254700000001",
				"role": Profile.Role.FARMER,
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		user = serializer.save()

		self.assertEqual(user.username, "farmer1")
		self.assertTrue(Profile.objects.filter(user=user, full_name="Farmer One").exists())


class AccountSerializerTests(TestCase):
	def test_account_serializer_updates_profile(self):
		user = User.objects.create_user(username="member", email="member@example.com", password="strong-pass-123")
		Profile.objects.create(user=user, full_name="Member One")
		serializer = AccountSerializer(
			instance=user,
			data={"first_name": "Member", "profile": {"full_name": "Updated Member", "preferred_language": "sw"}},
			partial=True,
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		updated_user = serializer.save()

		self.assertEqual(updated_user.first_name, "Member")
		self.assertEqual(updated_user.profile.full_name, "Updated Member")
