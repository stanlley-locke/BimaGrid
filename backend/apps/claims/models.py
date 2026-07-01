"""Claims domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class Claim(TimeStampedUUIDModel):
	class Status(models.TextChoices):
		DRAFT = "draft", "Draft"
		SUBMITTED = "submitted", "Submitted"
		UNDER_REVIEW = "under_review", "Under Review"
		APPROVED = "approved", "Approved"
		REJECTED = "rejected", "Rejected"

	policy = models.ForeignKey("policies.Policy", on_delete=models.PROTECT, related_name="claims")
	claim_number = models.CharField(max_length=40, unique=True)
	loss_type = models.CharField(max_length=64)
	description = models.TextField(blank=True)
	claimed_amount = models.DecimalField(max_digits=12, decimal_places=2)
	trigger_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	threshold_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	evidence = models.JSONField(default=dict, blank=True)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

	class Meta:
		ordering = ["-created_at"]
		indexes = [models.Index(fields=["claim_number"]), models.Index(fields=["status"])]

	def __str__(self) -> str:
		return self.claim_number


class ClaimReview(TimeStampedUUIDModel):
	claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="reviews")
	reviewed_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
	decision = models.CharField(max_length=32)
	notes = models.TextField(blank=True)
