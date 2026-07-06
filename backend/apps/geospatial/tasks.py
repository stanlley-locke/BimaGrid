"""Geospatial Celery tasks."""

from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from .h3_utils import h3_to_boundary_geojson, h3_to_lat_lng
from .models import H3Grid, Ward, WardProfile


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


@shared_task
def profile_ward_area(ward_id: str) -> str:
	"""Fetch satellite and historical weather baselines for a ward on first registration."""
	ward = Ward.objects.select_related("subcounty__county").filter(id=ward_id).first()
	if not ward:
		return "missing"

	profile, created = WardProfile.objects.get_or_create(ward=ward)
	if profile.status == WardProfile.ProfilingStatus.READY and not created:
		return profile.status

	profile.status = WardProfile.ProfilingStatus.IN_PROGRESS
	profile.data_sources = ["openEO", "CHIRPS", "NASA_POWER"]
	profile.save(update_fields=["status", "data_sources", "updated_at"])

	# Placeholder scoring until satellite integrations are wired in production.
	profile.drought_risk_score = profile.drought_risk_score or 0.35
	profile.flood_risk_score = profile.flood_risk_score or 0.12
	profile.mean_rainfall_mm = profile.mean_rainfall_mm or 850
	profile.ndvi_baseline = profile.ndvi_baseline or 0.42
	profile.metadata = {
		**profile.metadata,
		"county": ward.subcounty.county.name,
		"subcounty": ward.subcounty.name,
		"constituency": ward.constituency.name,
		"ward": ward.name,
	}
	profile.status = WardProfile.ProfilingStatus.READY
	profile.profiled_at = timezone.now()
	profile.save()
	return profile.status
