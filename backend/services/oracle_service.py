"""Oracle orchestration service."""

from __future__ import annotations

from apps.oracles.services import ingest_oracle_payload, simulate_drought_data
from apps.oracles.tasks import evaluate_h3_hexagon


def trigger_evaluation(h3_index: str, simulate_drought: bool = False) -> dict:
	if simulate_drought:
		return simulate_drought_data(h3_index, rainfall_mm=15.0, ndvi=0.35)
	task = evaluate_h3_hexagon.delay(h3_index, simulate_drought=False)
	return {"task_id": task.id, "h3_index": h3_index}


def submit_oracle_data(payload: dict, signature: str) -> dict:
	return ingest_oracle_payload(payload, signature)
