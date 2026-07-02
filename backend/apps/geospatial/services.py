"""Geospatial services."""

from __future__ import annotations

from .h3_utils import geojson_centroid, h3_index_from_geojson, h3_to_boundary_geojson
from .models import H3Grid, ParcelGeometry


def register_parcel_geometry(onboarding, geometry_data: dict) -> ParcelGeometry:
	geometry = geometry_data.get("geometry_geojson") or {}
	if geometry and not geometry_data.get("h3_index"):
		geometry_data["h3_index"] = h3_index_from_geojson(geometry)
	if geometry and not geometry_data.get("centroid"):
		lat, lng = geojson_centroid(geometry)
		geometry_data["centroid"] = {"lat": lat, "lng": lng}
	return ParcelGeometry.objects.create(onboarding=onboarding, **geometry_data)


def ensure_h3_grid(h3_index: str, resolution: int = 9, region_code: str = "") -> H3Grid:
	from .h3_utils import h3_to_lat_lng

	lat, lng = h3_to_lat_lng(h3_index)
	grid, _ = H3Grid.objects.update_or_create(
		h3_index=h3_index,
		defaults={
			"resolution": resolution,
			"centroid_lat": lat,
			"centroid_lng": lng,
			"boundary_geojson": h3_to_boundary_geojson(h3_index),
			"region_code": region_code,
		},
	)
	return grid
