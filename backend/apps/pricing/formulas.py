"""Actuarial pricing formulas."""

from __future__ import annotations

from decimal import Decimal


def apply_load_factor(base_premium: Decimal, load_factor: Decimal = Decimal("1.15")) -> Decimal:
	return (base_premium * load_factor).quantize(Decimal("0.01"))


def apply_mitigation_discount(
	base_premium: Decimal,
	discount_percent: Decimal,
	cap_percent: Decimal,
) -> Decimal:
	effective = min(discount_percent, cap_percent)
	return (base_premium * effective / Decimal("100")).quantize(Decimal("0.01"))


def peril_adjusted_premium(
	base_premium: Decimal,
	drought_multiplier: Decimal,
	flood_multiplier: Decimal,
	drought_weight: Decimal = Decimal("0.6"),
	flood_weight: Decimal = Decimal("0.4"),
) -> Decimal:
	combined = (drought_multiplier * drought_weight) + (flood_multiplier * flood_weight)
	return (base_premium * combined).quantize(Decimal("0.01"))


def risk_score_multiplier(risk_score: Decimal) -> Decimal:
	"""Map 0-1 risk score to premium multiplier (0.8 - 1.5)."""
	score = max(Decimal("0"), min(risk_score, Decimal("1")))
	return (Decimal("0.8") + score * Decimal("0.7")).quantize(Decimal("0.0001"))
