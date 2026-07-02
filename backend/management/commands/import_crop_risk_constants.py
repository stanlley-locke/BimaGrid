"""Import crop risk constants as pricing rules."""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.onboarding.constants import CropChoice
from apps.pricing.models import PricingRule
from apps.pricing.risk_matrices import CROP_BASE_RISK, CROP_DROUGHT_SENSITIVITY


CROP_BASE_RATES = {
	CropChoice.MAIZE: Decimal("180.00"),
	CropChoice.BEANS: Decimal("150.00"),
	CropChoice.SORGHUM: Decimal("120.00"),
	CropChoice.WHEAT: Decimal("165.00"),
	CropChoice.RICE: Decimal("200.00"),
	CropChoice.COFFEE: Decimal("250.00"),
	CropChoice.TEA: Decimal("230.00"),
	CropChoice.POTATO: Decimal("175.00"),
	CropChoice.MIXED: Decimal("160.00"),
}


class Command(BaseCommand):
	help = "Import crop risk constants and base pricing rules."

	def handle(self, *args, **options):
		count = 0
		for crop_choice in CropChoice:
			crop = crop_choice.value
			base_rate = CROP_BASE_RATES.get(crop_choice, Decimal("160.00"))
			drought_mult = CROP_DROUGHT_SENSITIVITY.get(crop, Decimal("1.0"))
			flood_mult = Decimal("1.0") + (CROP_BASE_RISK.get(crop, Decimal("0.5")) * Decimal("0.3"))
			PricingRule.objects.update_or_create(
				crop=crop,
				defaults={
					"base_rate_per_acre": base_rate,
					"drought_multiplier": drought_mult,
					"flood_multiplier": flood_mult.quantize(Decimal("0.01")),
					"mitigation_discount_cap": Decimal("15.00"),
					"active": True,
				},
			)
			count += 1
		self.stdout.write(self.style.SUCCESS(f"Imported {count} crop pricing rules"))
