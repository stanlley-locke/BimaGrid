"""Onboarding constants."""

from django.db import models


class CropChoice(models.TextChoices):
	MAIZE = "maize", "Maize"
	BEANS = "beans", "Beans"
	SORGHUM = "sorghum", "Sorghum"
	WHEAT = "wheat", "Wheat"
	RICE = "rice", "Rice"
	COFFEE = "coffee", "Coffee"
	TEA = "tea", "Tea"
	POTATO = "potato", "Potato"
	MIXED = "mixed", "Mixed Crops"


class OnboardingStatus(models.TextChoices):
	DRAFT = "draft", "Draft"
	SUBMITTED = "submitted", "Submitted"
	UNDER_REVIEW = "under_review", "Under Review"
	VERIFIED = "verified", "Verified"
	REJECTED = "rejected", "Rejected"


VERIFICATION_STAGES = (
	(1, "Profile linked"),
	(2, "Farm details captured"),
	(3, "Parcel evidence attached"),
	(4, "Supporting documents reviewed"),
	(5, "Onboarding verified"),
)
