"""Oracle data aggregation and consensus."""

from __future__ import annotations

import hashlib
import json
import statistics
from decimal import Decimal
from typing import Any

from django.conf import settings

from apps.core.constants import DROUGHT_RAINFALL_THRESHOLD_MM, ORACLE_CONSENSUS_THRESHOLD
from apps.core.exceptions import OracleSignatureError

from .models import OracleSubmission


def build_submission_hash(payload: dict[str, Any]) -> str:
	canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
	return hashlib.sha256(canonical.encode()).hexdigest()


def verify_oracle_signature(payload: dict[str, Any], signature: str) -> bool:
	if not settings.ORACLE_SIGNATURE_VERIFY:
		return True
	if signature.startswith("mock:"):
		return settings.DEBUG
	payload_hash = build_submission_hash(payload)
	for authorized in settings.ORACLE_AUTHORIZED_KEYS:
		expected = hashlib.sha256(f"{payload_hash}:{authorized}".encode()).hexdigest()
		if signature == expected or signature == f"0x{expected}":
			return True
	raise OracleSignatureError("Oracle signature verification failed.")


def median_of_submissions(submissions: list[OracleSubmission]) -> Decimal:
	values = [float(item.metric_value) for item in submissions]
	return Decimal(str(statistics.median(values))).quantize(Decimal("0.0001"))


def blend_rainfall_sources(sources: dict[str, float]) -> float:
	if not sources:
		return 0.0
	weights = {"chirps": 0.5, "nasa-power": 0.3, "open-meteo": 0.2, "sentinel-2": 0.4}
	total_weight = 0.0
	weighted_sum = 0.0
	for source, value in sources.items():
		weight = weights.get(source, 0.25)
		weighted_sum += value * weight
		total_weight += weight
	return weighted_sum / total_weight if total_weight else 0.0


def evaluate_drought_trigger(rainfall_mm: float, threshold_mm: float = DROUGHT_RAINFALL_THRESHOLD_MM) -> bool:
	return rainfall_mm < threshold_mm


def consensus_ready(h3_index: str, metric_name: str, round_number: int = 1) -> bool:
	count = OracleSubmission.objects.filter(
		h3_index=h3_index,
		metric_name=metric_name,
		consensus_round=round_number,
	).count()
	return count >= ORACLE_CONSENSUS_THRESHOLD


def aggregate_submissions(submissions: list[OracleSubmission]) -> dict[str, Any]:
	if not submissions:
		return {}
	by_metric: dict[str, list[OracleSubmission]] = {}
	for submission in submissions:
		by_metric.setdefault(submission.metric_name, []).append(submission)
	result: dict[str, Any] = {"metrics": {}, "oracle_count": len(submissions)}
	for metric_name, items in by_metric.items():
		median = median_of_submissions(items)
		result["metrics"][metric_name] = {
			"median": str(median),
			"sources": [item.oracle_name for item in items],
		}
	return result
