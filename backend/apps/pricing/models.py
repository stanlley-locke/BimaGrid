"""Pricing domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class PricingRule(TimeStampedUUIDModel):
	crop = models.CharField(max_length=32, unique=True)
	base_rate_per_acre = models.DecimalField(max_digits=12, decimal_places=2)
	drought_multiplier = models.DecimalField(max_digits=8, decimal_places=2, default=1)
	flood_multiplier = models.DecimalField(max_digits=8, decimal_places=2, default=1)
	mitigation_discount_cap = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ["crop"]


class PremiumQuote(TimeStampedUUIDModel):
	profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="premium_quotes")
	crop = models.CharField(max_length=32)
	acreage = models.DecimalField(max_digits=8, decimal_places=2)
	base_premium = models.DecimalField(max_digits=12, decimal_places=2)
	discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	final_premium = models.DecimalField(max_digits=12, decimal_places=2)
	risk_metadata = models.JSONField(default=dict, blank=True)
