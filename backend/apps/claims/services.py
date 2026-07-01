"""Claims services."""

from __future__ import annotations

from django.db import transaction

from apps.core.utils import build_reference_code

from .models import Claim, ClaimReview


@transaction.atomic
def open_claim(policy, claim_data: dict) -> Claim:
	claim_number = claim_data.pop("claim_number", None) or build_reference_code("CLM")
	claim = Claim.objects.create(policy=policy, claim_number=claim_number, **claim_data)
	ClaimReview.objects.create(claim=claim, decision=claim.status, notes="Claim created.")
	return claim
