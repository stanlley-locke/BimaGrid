"""Satellite Celery tasks."""

from __future__ import annotations

from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone

from apps.geospatial.h3_utils import h3_to_lat_lng

from .openeo_client import get_openeo_client
from .process_graphs import extent_from_centroid
from .services import record_observation, store_analysis


@shared_task
def fetch_ndvi_for_h3(h3_index: str) -> str:
	lat, lng = h3_to_lat_lng(h3_index)
	extent = extent_from_centroid(lat, lng)
	end = date.today()
	start = end - timedelta(days=14)
	client = get_openeo_client()
	result = client.compute_ndvi(h3_index, extent)
	observation = record_observation(
		{
			"h3_index": h3_index,
			"scene_id": f"NDVI-{h3_index[:8]}",
			"source": result.get("source", "openeo"),
			"metric_name": "ndvi",
			"metric_value": result.get("mean", 0),
			"observed_at": timezone.now(),
			"metadata": {**result, "temporal_extent": [start.isoformat(), end.isoformat()]},
		}
	)
	store_analysis(observation, {"analysis_type": "ndvi", "result": result, "confidence": 85})
	return str(observation.id)
