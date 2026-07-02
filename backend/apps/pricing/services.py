"""Pricing services."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from .engine import calculate_premium
from .models import PremiumQuote, PricingRule


@transaction.atomic
def calculate_quote(profile, quote_data: dict) -> PremiumQuote:
	h3_index = quote_data.get("h3_index") or quote_data.get("coverage_h3", "")
	mitigations = quote_data.pop("mitigations", [])
	result = calculate_premium(
		crop=quote_data["crop"],
		acreage=quote_data["acreage"],
		h3_index=h3_index,
		mitigations=mitigations,
	)
	return PremiumQuote.objects.create(
		profile=profile,
		base_premium=result["base_premium"],
		discount_amount=result["discount_amount"],
		final_premium=result["final_premium"],
		risk_metadata=result["risk_metadata"],
		**quote_data,
	)
