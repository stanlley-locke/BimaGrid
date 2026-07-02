"""H3 spatial indexing utilities."""

from __future__ import annotations

from typing import Any

import h3
from django.conf import settings


def lat_lng_to_h3(lat: float, lng: float, resolution: int | None = None) -> str:
	res = resolution if resolution is not None else settings.H3_DEFAULT_RESOLUTION
	return h3.latlng_to_cell(lat, lng, res)


def h3_to_lat_lng(h3_index: str) -> tuple[float, float]:
	return h3.cell_to_latlng(h3_index)


def h3_to_boundary_geojson(h3_index: str) -> dict[str, Any]:
	boundary = h3.cell_to_boundary(h3_index)
	ring = [[lng, lat] for lat, lng in boundary]
	ring.append(ring[0])
	return {"type": "Polygon", "coordinates": [ring]}


def geojson_centroid(geometry: dict[str, Any]) -> tuple[float, float]:
	if geometry.get("type") == "Point":
		coords = geometry["coordinates"]
		return float(coords[1]), float(coords[0])
	if geometry.get("type") == "Polygon":
		ring = geometry["coordinates"][0]
	elif geometry.get("type") == "MultiPolygon":
		ring = geometry["coordinates"][0][0]
	else:
		raise ValueError(f"Unsupported geometry type: {geometry.get('type')}")
	lats = [point[1] for point in ring]
	lngs = [point[0] for point in ring]
	return sum(lats) / len(lats), sum(lngs) / len(lngs)


def h3_index_from_geojson(geometry: dict[str, Any], resolution: int | None = None) -> str:
	lat, lng = geojson_centroid(geometry)
	return lat_lng_to_h3(lat, lng, resolution)


def k_ring_indices(h3_index: str, k: int = 1) -> list[str]:
	return list(h3.grid_disk(h3_index, k))


def compact_indices(h3_indices: list[str]) -> list[str]:
	return list(h3.compact_cells(h3_indices))


def polyfill_geojson(geometry: dict[str, Any], resolution: int | None = None) -> list[str]:
	res = resolution if resolution is not None else settings.H3_DEFAULT_RESOLUTION
	if geometry.get("type") in {"Polygon", "MultiPolygon"}:
		h3shape = h3.geo_to_h3shape(geometry)
		return list(h3.polygon_to_cells(h3shape, res))
	lat, lng = geojson_centroid(geometry)
	return [lat_lng_to_h3(lat, lng, res)]
