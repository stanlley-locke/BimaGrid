"""Onboarding services."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Profile
from integrations.ardhisasa import ArdhiSasaClient
from integrations.iprs import IPRSClient

from .constants import OnboardingStatus
from .models import FarmerOnboarding, LandParcel


def get_or_create_onboarding(profile: Profile) -> FarmerOnboarding:
	onboarding, _ = FarmerOnboarding.objects.get_or_create(profile=profile)
	return onboarding


def verify_farmer_identity(profile: Profile, id_number: str, first_name: str, last_name: str, dob: str) -> dict:
	result = IPRSClient().verify_identity(id_number, first_name, last_name, dob)
	if result.get("status") == "verified":
		profile.national_id = id_number
		profile.save(update_fields=["national_id", "updated_at"])
	return result


def verify_land_parcel(title_number: str, owner_id_number: str, parcel_number: str) -> dict:
	return ArdhiSasaClient().verify_title(title_number, owner_id_number, parcel_number)


def calculate_verification_level(onboarding: FarmerOnboarding) -> int:
	level = 1
	if onboarding.ward_code and onboarding.crop and onboarding.acreage and onboarding.mpesa_number:
		level = 2
	parcels = list(onboarding.land_parcels.all())
	if parcels:
		level = 3
	if parcels and any(parcel.ownership_docs for parcel in parcels):
		level = 4
	if onboarding.status in {OnboardingStatus.SUBMITTED, OnboardingStatus.UNDER_REVIEW, OnboardingStatus.VERIFIED}:
		level = 5
	return level


def refresh_onboarding_level(onboarding: FarmerOnboarding) -> FarmerOnboarding:
	onboarding.verification_level = calculate_verification_level(onboarding)
	onboarding.save(update_fields=["verification_level", "updated_at"])
	return onboarding


@transaction.atomic
def replace_land_parcels(onboarding: FarmerOnboarding, parcels_data: list[dict]) -> list[LandParcel]:
	onboarding.land_parcels.all().delete()
	land_parcels = [LandParcel(onboarding=onboarding, **parcel_data) for parcel_data in parcels_data]
	LandParcel.objects.bulk_create(land_parcels)
	return land_parcels


@transaction.atomic
def submit_onboarding(onboarding: FarmerOnboarding) -> FarmerOnboarding:
	onboarding.status = OnboardingStatus.SUBMITTED
	onboarding.submitted_at = timezone.now()
	onboarding.verification_level = max(onboarding.verification_level, 5)
	onboarding.save(update_fields=["status", "submitted_at", "verification_level", "updated_at"])
	return onboarding
