"""Pricing services."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from .models import PremiumQuote, PricingRule


@transaction.atomic
def calculate_quote(profile, quote_data: dict) -> PremiumQuote:
	rule = PricingRule.objects.filter(crop=quote_data["crop"], active=True).first()
	base_rate = rule.base_rate_per_acre if rule else Decimal("0.00")
	acreage = quote_data["acreage"]
	base_premium = (base_rate * acreage).quantize(Decimal("0.01"))
	discount_amount = Decimal("0.00")
	if rule:
		discount_amount = (base_premium * (rule.mitigation_discount_cap / Decimal("100"))).quantize(Decimal("0.01"))
	final_premium = max(base_premium - discount_amount, Decimal("0.00"))
	return PremiumQuote.objects.create(
		profile=profile,
		base_premium=base_premium,
		discount_amount=discount_amount,
		final_premium=final_premium,
		**quote_data,
	)