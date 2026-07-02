"""Geospatial Celery tasks."""

from __future__ import annotations

from celery import shared_task

from .h3_utils import h3_to_boundary_geojson, h3_to_lat_lng
from .models import H3Grid


@shared_task
def index_h3_cell(h3_index: str, resolution: int = 9, region_code: str = "") -> str:
	lat, lng = h3_to_lat_lng(h3_index)
	H3Grid.objects.update_or_create(
		h3_index=h3_index,
		defaults={
			"resolution": resolution,
			"centroid_lat": lat,
			"centroid_lng": lng,
			"boundary_geojson": h3_to_boundary_geojson(h3_index),
			"region_code": region_code,
		},
	)
	return h3_index
