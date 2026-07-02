"""Verification Celery tasks."""

from __future__ import annotations

from celery import shared_task

from .models import VerificationRecord
from .satellite import verify_irrigation
from .services import mark_verification_reviewed


@shared_task
def run_mitigation_verification(record_id: str) -> dict:
	record = VerificationRecord.objects.select_related("onboarding").get(id=record_id)
	parcel = record.onboarding.land_parcels.filter(is_primary=True).first()
	h3_index = parcel.h3_index if parcel else ""
	result = verify_irrigation(h3_index) if h3_index else {"verified": False, "reason": "no_parcel"}
	status = VerificationRecord.Status.APPROVED if result.get("verified") else VerificationRecord.Status.REJECTED
	mark_verification_reviewed(record, reviewer=None, status=status, findings=str(result))
	return result
