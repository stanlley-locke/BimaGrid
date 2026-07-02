"""Backend test utilities."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.accounts.services import get_or_create_profile
from apps.onboarding.constants import CropChoice, OnboardingStatus
from apps.onboarding.models import FarmerOnboarding
from apps.policies.models import Policy

User = get_user_model()


def authenticated_client(user) -> APIClient:
	client = APIClient()
	client.force_authenticate(user=user)
	return client


def token_client(user) -> APIClient:
	token, _ = Token.objects.get_or_create(user=user)
	client = APIClient()
	client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
	return client


def create_user_with_profile(username: str = "testuser", **profile_kwargs) -> tuple:
	user = User.objects.create_user(
		username=username,
		email=f"{username}@example.com",
		password="test-pass-123",
	)
	profile = get_or_create_profile(user)
	for field, value in profile_kwargs.items():
		setattr(profile, field, value)
	profile.save()
	onboarding = FarmerOnboarding.objects.get(profile=profile)
	return user, profile, onboarding


def create_admin_user(username: str = "admin") -> tuple:
	user = User.objects.create_user(
		username=username,
		email=f"{username}@example.com",
		password="test-pass-123",
		is_staff=True,
	)
	profile, _ = Profile.objects.get_or_create(
		user=user,
		defaults={"full_name": "Admin", "role": Profile.Role.ADMIN},
	)
	if profile.role != Profile.Role.ADMIN:
		profile.role = Profile.Role.ADMIN
		profile.save(update_fields=["role", "updated_at"])
	return user, profile


def create_policy_for_profile(profile: Profile, **overrides) -> Policy:
	onboarding = getattr(profile, "onboarding", None)
	if not onboarding:
		onboarding = FarmerOnboarding.objects.create(profile=profile)
	onboarding.ward_code = onboarding.ward_code or "1234"
	onboarding.crop = onboarding.crop or CropChoice.MAIZE
	onboarding.acreage = onboarding.acreage or Decimal("2.5")
	onboarding.status = OnboardingStatus.VERIFIED
	onboarding.save()

	defaults = {
		"onboarding": onboarding,
		"policy_number": f"POL-{profile.user.username.upper()}",
		"crop": CropChoice.MAIZE,
		"insured_acreage": Decimal("2.5"),
		"coverage_h3": "8928308280fffff",
		"premium_amount": Decimal("250.00"),
		"coverage_start": date.today(),
		"coverage_end": date.today() + timedelta(days=180),
		"status": Policy.Status.DRAFT,
	}
	defaults.update(overrides)
	return Policy.objects.create(**defaults)
