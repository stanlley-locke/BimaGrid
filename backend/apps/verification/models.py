"""Verification domain models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedUUIDModel


class VerificationRecord(TimeStampedUUIDModel):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		IN_REVIEW = "in_review", "In Review"
		APPROVED = "approved", "Approved"
		REJECTED = "rejected", "Rejected"

	onboarding = models.ForeignKey("onboarding.FarmerOnboarding", on_delete=models.CASCADE, related_name="verification_records")
	verification_type = models.CharField(max_length=64, default="identity")
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	findings = models.TextField(blank=True)
	reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verification_reviews")
	reviewed_at = models.DateTimeField(null=True, blank=True)


class VerificationArtifact(TimeStampedUUIDModel):
	record = models.ForeignKey(VerificationRecord, on_delete=models.CASCADE, related_name="artifacts")
	artifact_type = models.CharField(max_length=64)
	uri = models.CharField(max_length=255)
	checksum = models.CharField(max_length=128, blank=True)
