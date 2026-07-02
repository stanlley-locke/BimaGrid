"""Satellite verification via openEO."""

from __future__ import annotations

from datetime import date, timedelta

from apps.geospatial.h3_utils import h3_to_lat_lng
from apps.satellite.openeo_client import get_openeo_client
from apps.satellite.process_graphs import extent_from_centroid


def verify_irrigation(h3_index: str, threshold: float = 0.35) -> dict:
	lat, lng = h3_to_lat_lng(h3_index)
	extent = extent_from_centroid(lat, lng)
	end = date.today()
	start = end - timedelta(days=30)
	client = get_openeo_client()
	result = client.compute_ndwi(h3_index, extent)
	mean_ndwi = float(result.get("mean", 0))
	return {
		"h3_index": h3_index,
		"mean_ndwi": mean_ndwi,
		"verified": mean_ndwi >= threshold,
		"mitigation": "drip_irrigation",
		"source": result.get("source", "openeo"),
		"temporal_extent": [start.isoformat(), end.isoformat()],
	}
