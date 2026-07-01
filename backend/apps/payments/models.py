"""Payments domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class PaymentTransaction(TimeStampedUUIDModel):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		PROCESSING = "processing", "Processing"
		SUCCESS = "success", "Success"
		FAILED = "failed", "Failed"

	policy = models.ForeignKey("policies.Policy", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
	claim = models.ForeignKey("claims.Claim", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
	provider = models.CharField(max_length=64, default="mpesa")
	reference = models.CharField(max_length=64, unique=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	currency = models.CharField(max_length=8, default="KES")
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	provider_payload = models.JSONField(default=dict, blank=True)
	processed_at = models.DateTimeField(null=True, blank=True)


class Payout(TimeStampedUUIDModel):
	policy = models.ForeignKey("policies.Policy", on_delete=models.PROTECT, related_name="payouts")
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	phone_number = models.CharField(max_length=32)
	reference = models.CharField(max_length=64, unique=True)
	status = models.CharField(max_length=16, default="queued")
	tx_hash = models.CharField(max_length=128, blank=True)
