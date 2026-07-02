"""Geospatial domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class H3Grid(TimeStampedUUIDModel):
	resolution = models.PositiveSmallIntegerField(default=9)
	h3_index = models.CharField(max_length=32, unique=True, db_index=True)
	centroid_lat = models.DecimalField(max_digits=9, decimal_places=6)
	centroid_lng = models.DecimalField(max_digits=9, decimal_places=6)
	boundary_geojson = models.JSONField(default=dict, blank=True)
	region_code = models.CharField(max_length=32, blank=True)

	class Meta:
		ordering = ["h3_index"]
		indexes = [models.Index(fields=["resolution", "h3_index"])]

	def __str__(self) -> str:
		return self.h3_index


class GridRisk(TimeStampedUUIDModel):
	h3_index = models.CharField(max_length=32, db_index=True)
	mean_rainfall_mm = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	flood_threshold_mm = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	frost_days = models.PositiveIntegerField(default=0)
	heat_stress_days = models.PositiveIntegerField(default=0)
	drought_risk_score = models.DecimalField(max_digits=6, decimal_places=4, default=0)
	flood_risk_score = models.DecimalField(max_digits=6, decimal_places=4, default=0)
	metadata = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ["h3_index"]
		indexes = [models.Index(fields=["h3_index"])]
		unique_together = [("h3_index",)]

	def __str__(self) -> str:
		return f"Risk({self.h3_index})"


class ParcelGeometry(TimeStampedUUIDModel):
	onboarding = models.ForeignKey("onboarding.FarmerOnboarding", on_delete=models.CASCADE, related_name="parcel_geometries")
	name = models.CharField(max_length=255, blank=True)
	h3_index = models.CharField(max_length=32, db_index=True)
	ward_code = models.CharField(max_length=32, blank=True)
	geometry_geojson = models.JSONField(default=dict)
	centroid = models.JSONField(default=dict, blank=True)
	acreage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	source = models.CharField(max_length=64, default="manual")
