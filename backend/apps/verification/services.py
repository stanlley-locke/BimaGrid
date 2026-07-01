"""Verification services."""

from __future__ import annotations

from django.utils import timezone

from .models import VerificationRecord


def create_verification_record(onboarding, verification_data: dict) -> VerificationRecord:
	return VerificationRecord.objects.create(onboarding=onboarding, **verification_data)


def mark_verification_reviewed(record: VerificationRecord, reviewer, status: str, findings: str = "") -> VerificationRecord:
	record.status = status
	record.reviewed_by = reviewer
	record.reviewed_at = timezone.now()
	record.findings = findings
	record.save(update_fields=["status", "reviewed_by", "reviewed_at", "findings", "updated_at"])
	return record
