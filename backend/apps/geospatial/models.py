"""Geospatial domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class ParcelGeometry(TimeStampedUUIDModel):
	onboarding = models.ForeignKey("onboarding.FarmerOnboarding", on_delete=models.CASCADE, related_name="parcel_geometries")
	name = models.CharField(max_length=255, blank=True)
	h3_index = models.CharField(max_length=32, db_index=True)
	ward_code = models.CharField(max_length=32, blank=True)
	geometry_geojson = models.JSONField(default=dict)
	centroid = models.JSONField(default=dict, blank=True)
	acreage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	source = models.CharField(max_length=64, default="manual")
