"""Policy domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.onboarding.constants import CropChoice


class Policy(TimeStampedUUIDModel):
	class Status(models.TextChoices):
		DRAFT = "draft", "Draft"
		ACTIVE = "active", "Active"
		LAPSED = "lapsed", "Lapsed"
		CANCELLED = "cancelled", "Cancelled"

	onboarding = models.ForeignKey("onboarding.FarmerOnboarding", on_delete=models.PROTECT, related_name="policies")
	policy_number = models.CharField(max_length=40, unique=True)
	crop = models.CharField(max_length=32, choices=CropChoice.choices)
	insured_acreage = models.DecimalField(max_digits=8, decimal_places=2)
	coverage_h3 = models.CharField(max_length=32, db_index=True)
	premium_amount = models.DecimalField(max_digits=12, decimal_places=2)
	coverage_start = models.DateField()
	coverage_end = models.DateField()
	mitigation_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
	metadata = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [models.Index(fields=["policy_number"]), models.Index(fields=["coverage_h3"])]

	def __str__(self) -> str:
		return self.policy_number


class PolicyEvent(TimeStampedUUIDModel):
	policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="events")
	event_type = models.CharField(max_length=64)
	details = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ["-created_at"]
