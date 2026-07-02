"""openEO process graph definitions for NDVI/NDWI."""

from __future__ import annotations

from datetime import date
from typing import Any


def ndvi_process_graph(spatial_extent: dict[str, float], temporal_extent: tuple[date, date]) -> dict[str, Any]:
	return {
		"loadcollection1": {
			"process_id": "load_collection",
			"arguments": {
				"id": "SENTINEL2_L2A",
				"spatial_extent": spatial_extent,
				"temporal_extent": [d.isoformat() for d in temporal_extent],
				"bands": ["B04", "B08"],
			},
		},
		"ndvi": {
			"process_id": "ndvi",
			"arguments": {"data": {"from_node": "loadcollection1"}, "red": "B04", "nir": "B08"},
		},
		"aggregate": {
			"process_id": "aggregate_spatial",
			"arguments": {"data": {"from_node": "ndvi"}, "reducer": "mean"},
		},
	}


def ndwi_process_graph(spatial_extent: dict[str, float], temporal_extent: tuple[date, date]) -> dict[str, Any]:
	return {
		"loadcollection1": {
			"process_id": "load_collection",
			"arguments": {
				"id": "SENTINEL2_L2A",
				"spatial_extent": spatial_extent,
				"temporal_extent": [d.isoformat() for d in temporal_extent],
				"bands": ["B03", "B08"],
			},
		},
		"ndwi": {
			"process_id": "normalized_difference",
			"arguments": {
				"data": {"from_node": "loadcollection1"},
				"x": "B03",
				"y": "B08",
			},
		},
		"aggregate": {
			"process_id": "aggregate_spatial",
			"arguments": {"data": {"from_node": "ndwi"}, "reducer": "mean"},
		},
	}


def extent_from_centroid(lat: float, lng: float, delta: float = 0.01) -> dict[str, float]:
	return {
		"west": lng - delta,
		"south": lat - delta,
		"east": lng + delta,
		"north": lat + delta,
	}


def evi_process_graph(spatial_extent: dict[str, float], temporal_extent: tuple[date, date]) -> dict[str, Any]:
	return {
		"loadcollection1": {
			"process_id": "load_collection",
			"arguments": {
				"id": "SENTINEL2_L2A",
				"spatial_extent": spatial_extent,
				"temporal_extent": [d.isoformat() for d in temporal_extent],
				"bands": ["B02", "B04", "B08"],
			},
		},
		"evi": {
			"process_id": "evi",
			"arguments": {
				"data": {"from_node": "loadcollection1"},
				"blue": "B02",
				"red": "B04",
				"nir": "B08"
			},
		},
		"aggregate": {
			"process_id": "aggregate_spatial",
			"arguments": {"data": {"from_node": "evi"}, "reducer": "mean"},
		},
	}

