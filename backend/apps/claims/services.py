"""Claims services."""

from __future__ import annotations

from django.db import transaction

from apps.core.utils import build_reference_code
from apps.oracles.aggregators import evaluate_drought_trigger

from .models import Claim, ClaimReview


@transaction.atomic
def open_claim(policy, claim_data: dict) -> Claim:
	claim_number = claim_data.pop("claim_number", None) or build_reference_code("CLM")
	claim = Claim.objects.create(policy=policy, claim_number=claim_number, **claim_data)
	ClaimReview.objects.create(claim=claim, decision=claim.status, notes="Claim created.")
	return claim


@transaction.atomic
def evaluate_parametric_claim(claim: Claim, observed_value: float) -> Claim:
	triggered = evaluate_drought_trigger(observed_value, float(claim.threshold_value or 30))
	claim.trigger_value = observed_value
	if triggered:
		claim.status = Claim.Status.APPROVED
		decision = "approved"
	else:
		claim.status = Claim.Status.REJECTED
		decision = "rejected"
	claim.save(update_fields=["trigger_value", "status", "updated_at"])
	ClaimReview.objects.create(
		claim=claim,
		decision=decision,
		notes=f"Parametric evaluation: observed={observed_value}, threshold={claim.threshold_value}",
	)
	return claim
