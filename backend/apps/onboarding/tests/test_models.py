from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Profile
from apps.onboarding.models import FarmerOnboarding, LandParcel


User = get_user_model()


class OnboardingModelTests(TestCase):
	def test_profile_creation_creates_onboarding(self):
		user = User.objects.create_user(username="farmer", email="farmer@example.com", password="strong-pass-123")
		profile = Profile.objects.create(user=user, full_name="Farmer One")

		self.assertTrue(FarmerOnboarding.objects.filter(profile=profile).exists())

	def test_land_parcel_string_uses_name_or_h3(self):
		user = User.objects.create_user(username="parcel", email="parcel@example.com", password="strong-pass-123")
		profile = Profile.objects.create(user=user, full_name="Parcel Farmer")
		onboarding = FarmerOnboarding.objects.get(profile=profile)
		parcel = LandParcel.objects.create(onboarding=onboarding, name="North Field", h3_index="8928308280fffff", geometry_geojson={"type": "Polygon", "coordinates": []}, acreage=2.5)

		self.assertEqual(str(parcel), "North Field")