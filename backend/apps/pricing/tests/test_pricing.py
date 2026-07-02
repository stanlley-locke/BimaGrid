import pytest
from decimal import Decimal

from apps.pricing.models import PricingRule
from apps.pricing.formulas import (
    apply_load_factor,
    apply_mitigation_discount,
    peril_adjusted_premium,
    risk_score_multiplier
)
from apps.pricing.engine import calculate_premium


class TestPricingFormulas:
    def test_apply_load_factor(self):
        base = Decimal("100.00")
        assert apply_load_factor(base, Decimal("1.10")) == Decimal("110.00")

    def test_apply_mitigation_discount(self):
        base = Decimal("1000.00")
        # 10% discount, cap 15% -> 10% discount applied
        assert apply_mitigation_discount(base, Decimal("10"), Decimal("15")) == Decimal("100.00")
        
        # 20% discount, cap 15% -> 15% discount applied
        assert apply_mitigation_discount(base, Decimal("20"), Decimal("15")) == Decimal("150.00")

    def test_peril_adjusted_premium(self):
        base = Decimal("500.00")
        # combined = (1.2 * 0.6) + (0.8 * 0.4) = 0.72 + 0.32 = 1.04
        # premium = 500 * 1.04 = 520
        assert peril_adjusted_premium(
            base, Decimal("1.2"), Decimal("0.8")
        ) == Decimal("520.00")

    def test_risk_score_multiplier(self):
        # min limit
        assert risk_score_multiplier(Decimal("-0.5")) == Decimal("0.8000")
        # max limit
        assert risk_score_multiplier(Decimal("1.5")) == Decimal("1.5000")
        # midpoint
        assert risk_score_multiplier(Decimal("0.5")) == Decimal("1.1500")


@pytest.mark.django_db
class TestPricingEngine:
    def test_calculate_premium_default_success(self):
        PricingRule.objects.create(
            crop="MAIZE",
            base_rate_per_acre=Decimal("200.00"),
            drought_multiplier=Decimal("1.0"),
            flood_multiplier=Decimal("1.0"),
            mitigation_discount_cap=Decimal("15"),
            active=True
        )
        
        result = calculate_premium(
            crop="MAIZE",
            acreage=Decimal("2.5"),
            h3_index="8928308280fffff",
            mitigations=["drip_irrigation"]
        )
        
        assert result["base_premium"] == Decimal("500.00")
        assert result["final_premium"] >= Decimal("0.00")
        assert "risk_metadata" in result
        assert "drip_irrigation" in result["risk_metadata"]["mitigations"]

    def test_calculate_premium_case_insensitivity(self):
        PricingRule.objects.create(
            crop="MAIZE",
            base_rate_per_acre=Decimal("200.00"),
            drought_multiplier=Decimal("1.0"),
            flood_multiplier=Decimal("1.0"),
            mitigation_discount_cap=Decimal("15"),
            active=True
        )
        
        result_upper = calculate_premium(
            crop="MAIZE",
            acreage=Decimal("1.0"),
            h3_index="8928308280fffff"
        )
        
        result_lower = calculate_premium(
            crop="maize",
            acreage=Decimal("1.0"),
            h3_index="8928308280fffff"
        )
        
        assert result_upper["risk_metadata"]["crop_risk_score"] == "0.55"
        assert result_lower["risk_metadata"]["crop_risk_score"] == "0.55"

