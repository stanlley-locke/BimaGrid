"""Pricing orchestration service."""

from __future__ import annotations

from decimal import Decimal

from apps.accounts.models import Profile
from apps.pricing.engine import calculate_premium
from apps.pricing.models import PremiumQuote


def create_quote_for_profile(
	profile: Profile,
	crop: str,
	acreage: Decimal,
	h3_index: str,
	mitigations: list[str] | None = None,
) -> PremiumQuote:
	result = calculate_premium(crop, acreage, h3_index, mitigations=mitigations)
	return PremiumQuote.objects.create(
		profile=profile,
		crop=crop,
		acreage=acreage,
		base_premium=result["base_premium"],
		discount_amount=result["discount_amount"],
		final_premium=result["final_premium"],
		risk_metadata=result["risk_metadata"],
	)
