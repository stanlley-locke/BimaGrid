"""Shared test factories."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile
from apps.onboarding.constants import CropChoice, OnboardingStatus
from apps.onboarding.models import FarmerOnboarding, LandParcel
from apps.policies.models import Policy

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = User

	username = factory.Sequence(lambda n: f"user{n}")
	email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
	password = factory.PostGenerationMethodCall("set_password", "test-pass-123")


class ProfileFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Profile

	user = factory.SubFactory(UserFactory)
	full_name = factory.Faker("name")
	phone_number = factory.Sequence(lambda n: f"2547{n:08d}")
	role = Profile.Role.FARMER


class FarmerOnboardingFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = FarmerOnboarding
		django_get_or_create = ("profile",)

	profile = factory.SubFactory(ProfileFactory)
	ward_code = "1234"
	crop = CropChoice.MAIZE
	acreage = Decimal("2.50")
	mpesa_number = factory.LazyAttribute(lambda obj: obj.profile.phone_number)
	status = OnboardingStatus.DRAFT


class LandParcelFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = LandParcel

	onboarding = factory.SubFactory(FarmerOnboardingFactory)
	h3_index = "8928308280fffff"
	acreage = Decimal("2.50")
	is_primary = True


class PolicyFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Policy

	onboarding = factory.SubFactory(FarmerOnboardingFactory)
	policy_number = factory.Sequence(lambda n: f"POL-TEST-{n:04d}")
	crop = CropChoice.MAIZE
	insured_acreage = Decimal("2.50")
	coverage_h3 = "8928308280fffff"
	premium_amount = Decimal("250.00")
	coverage_start = factory.LazyFunction(date.today)
	coverage_end = factory.LazyFunction(lambda: date.today() + timedelta(days=180))
	status = Policy.Status.DRAFT
