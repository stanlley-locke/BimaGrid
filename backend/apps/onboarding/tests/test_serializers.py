from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Profile
from apps.onboarding.constants import CropChoice
from apps.onboarding.serializers import FarmerOnboardingSerializer


User = get_user_model()


class OnboardingSerializerTests(TestCase):
	def test_serializer_creates_onboarding_with_parcels(self):
		user = User.objects.create_user(username="serializer", email="serializer@example.com", password="strong-pass-123")
		profile = Profile.objects.create(user=user, full_name="Serializer Farmer")

		serializer = FarmerOnboardingSerializer(
			data={
				"ward_code": "WARD-001",
				"crop": CropChoice.MAIZE,
				"acreage": "2.50",
				"mpesa_number": "254712345678",
				"land_parcels": [
					{
						"name": "Main Parcel",
						"ward_code": "WARD-001",
						"h3_index": "8928308280fffff",
						"geometry_geojson": {"type": "Polygon", "coordinates": []},
						"ownership_docs": [{"type": "title_deed", "reference": "TD-001"}],
						"acreage": "2.50",
						"is_primary": True,
					}
				],
			},
			context={"profile": profile},
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		onboarding = serializer.save()

		self.assertEqual(onboarding.profile, profile)
		self.assertEqual(onboarding.land_parcels.count(), 1)
		self.assertGreaterEqual(onboarding.verification_level, 3)