"""Onboarding domain models."""

from __future__ import annotations

import uuid

from django.db import models

from apps.accounts.models import Profile

from .constants import CropChoice, OnboardingStatus, VERIFICATION_STAGES


class TimeStampedUUIDModel(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class FarmerOnboarding(TimeStampedUUIDModel):
	profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="onboarding")
	ward_code = models.CharField(max_length=32, blank=True)
	crop = models.CharField(max_length=32, choices=CropChoice.choices, blank=True)
	acreage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	mpesa_number = models.CharField(max_length=32, blank=True)
	verification_level = models.PositiveSmallIntegerField(default=1)
	status = models.CharField(max_length=16, choices=OnboardingStatus.choices, default=OnboardingStatus.DRAFT)
	notes = models.TextField(blank=True)
	submitted_at = models.DateTimeField(null=True, blank=True)
	approved_at = models.DateTimeField(null=True, blank=True)
	rejection_reason = models.TextField(blank=True)

	class Meta:
		ordering = ["-updated_at"]

	def __str__(self) -> str:
		return f"Onboarding for {self.profile}"

	def stage_label(self) -> str:
		return dict(VERIFICATION_STAGES).get(self.verification_level, "Unknown stage")


class LandParcel(TimeStampedUUIDModel):
	onboarding = models.ForeignKey(FarmerOnboarding, on_delete=models.CASCADE, related_name="land_parcels")
	name = models.CharField(max_length=255, blank=True)
	ward_code = models.CharField(max_length=32, blank=True)
	h3_index = models.CharField(max_length=32, db_index=True)
	geometry_geojson = models.JSONField(default=dict)
	ownership_docs = models.JSONField(default=list, blank=True)
	acreage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	is_primary = models.BooleanField(default=False)
	verified = models.BooleanField(default=False)

	class Meta:
		ordering = ["-is_primary", "name", "created_at"]
		indexes = [models.Index(fields=["h3_index"])]

	def __str__(self) -> str:
		return self.name or self.h3_index
