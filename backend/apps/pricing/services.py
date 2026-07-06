"""Pricing services."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from .engine import calculate_premium
from .models import PremiumQuote, PricingRule


@transaction.atomic
def calculate_quote(profile, quote_data: dict) -> PremiumQuote:
	h3_index = quote_data.pop("h3_index", None) or quote_data.pop("coverage_h3", "")
	if not h3_index:
		h3_index = "8928308280fffff"
	mitigations = quote_data.pop("mitigations", [])
	
	from decimal import Decimal
	# Only keep valid model fields for quote_data
	crop = quote_data.pop("crop", "MAIZE")
	acreage_raw = quote_data.pop("acreage", 0)
	acreage = Decimal(str(acreage_raw))
	
	result = calculate_premium(
		crop=crop,
		acreage=acreage,
		h3_index=h3_index,
		mitigations=mitigations,
	)
	return PremiumQuote.objects.create(
		profile=profile,
		crop=crop,
		acreage=acreage,
		base_premium=result["base_premium"],
		discount_amount=result["discount_amount"],
		final_premium=result["final_premium"],
		risk_metadata=result["risk_metadata"],
	)
