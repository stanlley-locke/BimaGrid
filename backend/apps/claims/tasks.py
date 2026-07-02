"""Claims Celery tasks."""

from __future__ import annotations

from celery import shared_task

from apps.oracles.models import OracleConsensus
from apps.payments.services import queue_payout

from .models import Claim
from .services import evaluate_parametric_claim


@shared_task
def evaluate_claim_against_consensus(claim_id: str) -> dict:
	claim = Claim.objects.select_related("policy").get(id=claim_id)
	consensus = (
		OracleConsensus.objects.filter(h3_index=claim.policy.coverage_h3, metric_name="rainfall_mm")
		.order_by("-created_at")
		.first()
	)
	observed = float(consensus.consensus_value) if consensus else 0.0
	claim = evaluate_parametric_claim(claim, observed)
	result = {"claim_id": str(claim.id), "status": claim.status}
	if claim.status == Claim.Status.APPROVED:
		payout = queue_payout(claim.policy, claim.claimed_amount, claim.policy.onboarding.mpesa_number)
		result["payout_id"] = str(payout.id)
	return result
