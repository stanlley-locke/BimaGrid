"""Oracle services."""

from __future__ import annotations

import hashlib
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.core.constants import ORACLE_CONSENSUS_THRESHOLD

from .aggregators import (
	aggregate_submissions,
	build_submission_hash,
	consensus_ready,
	evaluate_drought_trigger,
	median_of_submissions,
	verify_oracle_signature,
)
from .models import OracleConsensus, OracleSubmission


def record_oracle_submission(submission_data: dict) -> OracleSubmission:
	payload = submission_data.get("payload") or {}
	signature = submission_data.get("signature", "")
	if payload:
		verify_oracle_signature(payload, signature)
		submission_data.setdefault("data_hash", build_submission_hash(payload))
	return OracleSubmission.objects.create(**submission_data)


def record_consensus(consensus_data: dict) -> OracleConsensus:
	return OracleConsensus.objects.create(**consensus_data)


@transaction.atomic
def ingest_oracle_payload(payload: dict[str, Any], signature: str) -> dict[str, Any]:
	verify_oracle_signature(payload, signature)
	h3_index = payload["h3_index"]
	round_number = payload.get("consensus_round", 1)
	oracle_id = payload["oracle_id"]
	timestamp = payload.get("timestamp", timezone.now().isoformat())

	metrics = {
		"rainfall_mm": Decimal(str(payload.get("rainfall_mm", 0))),
		"ndvi": Decimal(str(payload.get("ndvi", 0))),
		"soil_moisture": Decimal(str(payload.get("soil_moisture", 0))),
	}
	created = []
	for metric_name, metric_value in metrics.items():
		submission = OracleSubmission.objects.create(
			oracle_name=oracle_id,
			h3_index=h3_index,
			metric_name=metric_name,
			metric_value=metric_value,
			payload={**payload, "metric": metric_name},
			data_hash=build_submission_hash(payload),
			signature=signature,
			consensus_round=round_number,
		)
		created.append(submission)

	consensus_result = None
	if consensus_ready(h3_index, "rainfall_mm", round_number):
		submissions = list(
			OracleSubmission.objects.filter(
				h3_index=h3_index,
				metric_name="rainfall_mm",
				consensus_round=round_number,
			)
		)
		median_rainfall = median_of_submissions(submissions)
		consensus_result = OracleConsensus.objects.create(
			h3_index=h3_index,
			metric_name="rainfall_mm",
			consensus_value=median_rainfall,
			round_number=round_number,
			metadata=aggregate_submissions(submissions),
		)

	return {
		"submissions": [str(item.id) for item in created],
		"consensus": str(consensus_result.id) if consensus_result else None,
		"drought_triggered": evaluate_drought_trigger(float(median_rainfall)) if consensus_result else False,
		"timestamp": timestamp,
	}


def simulate_drought_data(h3_index: str, rainfall_mm: float, ndvi: float) -> dict[str, Any]:
	"""Create mock oracle submissions for demo God Mode."""
	submissions = []
	for oracle_id in ("oracle-1", "oracle-2", "oracle-3"):
		variation = {"oracle-1": 0, "oracle-2": 1.5, "oracle-3": -1.0}[oracle_id]
		payload = {
			"oracle_id": oracle_id,
			"h3_index": h3_index,
			"rainfall_mm": rainfall_mm + variation,
			"ndvi": ndvi,
			"soil_moisture": ndvi * 0.6,
			"data_sources": ["mock"],
		}
		signature = f"mock:{hashlib.sha256(oracle_id.encode()).hexdigest()[:16]}"
		result = ingest_oracle_payload(payload, signature)
		submissions.append(result)
	return {"h3_index": h3_index, "results": submissions}
