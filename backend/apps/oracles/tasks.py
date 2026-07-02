"""Oracle Celery tasks."""

from __future__ import annotations

from celery import shared_task

from .services import ingest_oracle_payload, simulate_drought_data


@shared_task
def process_oracle_submission(payload: dict, signature: str) -> dict:
	return ingest_oracle_payload(payload, signature)


@shared_task
def evaluate_h3_hexagon(h3_index: str, simulate_drought: bool = False) -> dict:
	if simulate_drought:
		return simulate_drought_data(h3_index, rainfall_mm=15.0, ndvi=0.35)
	payload = {
		"oracle_id": "celery-evaluator",
		"h3_index": h3_index,
		"rainfall_mm": 45.0,
		"ndvi": 0.65,
		"soil_moisture": 0.38,
		"data_sources": ["scheduled"],
	}
	return ingest_oracle_payload(payload, "mock:celery-evaluator")
