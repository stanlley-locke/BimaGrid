"""Pricing Celery tasks."""

from __future__ import annotations

from decimal import Decimal

from celery import shared_task

from apps.accounts.models import Profile

from .engine import calculate_premium
from .models import PremiumQuote


@shared_task
def generate_quote_async(profile_id: str, crop: str, acreage: str, h3_index: str, mitigations: list[str] | None = None) -> str:
	profile = Profile.objects.get(id=profile_id)
	result = calculate_premium(crop, Decimal(acreage), h3_index, mitigations=mitigations)
	quote = PremiumQuote.objects.create(
		profile=profile,
		crop=crop,
		acreage=Decimal(acreage),
		base_premium=result["base_premium"],
		discount_amount=result["discount_amount"],
		final_premium=result["final_premium"],
		risk_metadata=result["risk_metadata"],
	)
	return str(quote.id)
