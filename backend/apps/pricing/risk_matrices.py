"""Crop and peril risk lookup tables."""

from __future__ import annotations

from decimal import Decimal

CROP_BASE_RISK: dict[str, Decimal] = {
	"maize": Decimal("0.55"),
	"beans": Decimal("0.48"),
	"sorghum": Decimal("0.42"),
	"wheat": Decimal("0.50"),
	"rice": Decimal("0.58"),
	"coffee": Decimal("0.35"),
	"tea": Decimal("0.32"),
	"potato": Decimal("0.46"),
	"mixed": Decimal("0.52"),
}

CROP_DROUGHT_SENSITIVITY: dict[str, Decimal] = {
	"maize": Decimal("1.20"),
	"beans": Decimal("1.10"),
	"sorghum": Decimal("0.90"),
	"wheat": Decimal("1.05"),
	"rice": Decimal("1.15"),
	"coffee": Decimal("0.85"),
	"tea": Decimal("0.80"),
	"potato": Decimal("1.00"),
	"mixed": Decimal("1.05"),
}

MITIGATION_DISCOUNTS: dict[str, Decimal] = {
	"drip_irrigation": Decimal("12"),
	"mulching": Decimal("5"),
	"terracing": Decimal("8"),
	"cover_crop": Decimal("6"),
}


def crop_base_risk(crop: str) -> Decimal:
	return CROP_BASE_RISK.get(crop, Decimal("0.50"))


def crop_drought_sensitivity(crop: str) -> Decimal:
	return CROP_DROUGHT_SENSITIVITY.get(crop, Decimal("1.0"))


def mitigation_discount_percent(mitigations: list[str]) -> Decimal:
	total = Decimal("0")
	for item in mitigations:
		total += MITIGATION_DISCOUNTS.get(item, Decimal("0"))
	return min(total, Decimal("25"))
