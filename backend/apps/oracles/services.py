"""Oracle services."""

from __future__ import annotations

from .models import OracleConsensus, OracleSubmission


def record_oracle_submission(submission_data: dict) -> OracleSubmission:
	return OracleSubmission.objects.create(**submission_data)


def record_consensus(consensus_data: dict) -> OracleConsensus:
	return OracleConsensus.objects.create(**consensus_data)
