"""Policy issuance orchestration."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from apps.onboarding.models import FarmerOnboarding
from apps.policies.constants import DEFAULT_COVERAGE_DAYS
from apps.policies.models import Policy
from apps.policies.services import issue_policy
from apps.pricing.engine import calculate_premium


def issue_policy_from_onboarding(
	onboarding: FarmerOnboarding,
	mitigations: list[str] | None = None,
) -> Policy:
	parcel = onboarding.land_parcels.filter(is_primary=True).first() or onboarding.land_parcels.first()
	h3_index = parcel.h3_index if parcel else ""
	premium_result = calculate_premium(
		crop=onboarding.crop,
		acreage=onboarding.acreage,
		h3_index=h3_index,
		mitigations=mitigations or [],
	)
	start = date.today()
	end = start + timedelta(days=DEFAULT_COVERAGE_DAYS)
	return issue_policy(
		onboarding,
		{
			"crop": onboarding.crop,
			"insured_acreage": onboarding.acreage,
			"coverage_h3": h3_index,
			"premium_amount": premium_result["final_premium"],
			"coverage_start": start,
			"coverage_end": end,
			"mitigation_discount_percent": Decimal(premium_result["risk_metadata"].get("mitigation_discount_percent", "0")),
			"status": Policy.Status.DRAFT,
			"metadata": premium_result["risk_metadata"],
		},
	)
