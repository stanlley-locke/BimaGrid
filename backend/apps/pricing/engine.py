"""Actuarial premium calculation engine."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.geospatial.spatial_queries import average_risk_score, get_grid_risk

from .formulas import (
	apply_load_factor,
	apply_mitigation_discount,
	peril_adjusted_premium,
	risk_score_multiplier,
)
from .models import PricingRule
from .risk_matrices import crop_base_risk, crop_drought_sensitivity, mitigation_discount_percent


def calculate_premium(
	crop: str,
	acreage: Decimal,
	h3_index: str,
	mitigations: list[str] | None = None,
	rule: PricingRule | None = None,
) -> dict[str, Any]:
	mitigations = mitigations or []
	active_rule = rule or PricingRule.objects.filter(crop=crop, active=True).first()
	base_rate = active_rule.base_rate_per_acre if active_rule else Decimal("180.00")
	drought_mult = active_rule.drought_multiplier if active_rule else Decimal("1.0")
	flood_mult = active_rule.flood_multiplier if active_rule else Decimal("1.0")
	discount_cap = active_rule.mitigation_discount_cap if active_rule else Decimal("15")

	base_premium = (base_rate * acreage).quantize(Decimal("0.01"))
	grid_risk = get_grid_risk(h3_index)
	grid_score = grid_risk.drought_risk_score if grid_risk else average_risk_score(h3_index)
	crop_risk = crop_base_risk(crop)
	combined_risk = ((grid_score + crop_risk) / Decimal("2")).quantize(Decimal("0.0001"))
	risk_multiplier = risk_score_multiplier(combined_risk)
	drought_adj = drought_mult * crop_drought_sensitivity(crop)

	adjusted = peril_adjusted_premium(base_premium * risk_multiplier, drought_adj, flood_mult)
	loaded = apply_load_factor(adjusted)
	mitigation_pct = mitigation_discount_percent(mitigations)
	discount_amount = apply_mitigation_discount(loaded, mitigation_pct, discount_cap)
	final_premium = max(loaded - discount_amount, Decimal("0.00"))

	return {
		"base_premium": base_premium,
		"adjusted_premium": loaded,
		"discount_amount": discount_amount,
		"final_premium": final_premium,
		"risk_metadata": {
			"h3_index": h3_index,
			"grid_risk_score": str(grid_score),
			"crop_risk_score": str(crop_risk),
			"combined_risk_score": str(combined_risk),
			"risk_multiplier": str(risk_multiplier),
			"drought_multiplier": str(drought_adj),
			"flood_multiplier": str(flood_mult),
			"mitigations": mitigations,
			"mitigation_discount_percent": str(mitigation_pct),
		},
	}
