"""Geospatial domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class County(TimeStampedUUIDModel):
	external_id = models.PositiveIntegerField(unique=True, db_index=True)
	name = models.CharField(max_length=255)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "counties"

	def __str__(self) -> str:
		return self.name


class SubCounty(TimeStampedUUIDModel):
	external_id = models.PositiveIntegerField(unique=True, db_index=True)
	county = models.ForeignKey(County, on_delete=models.CASCADE, related_name="subcounties")
	name = models.CharField(max_length=255)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "subcounties"
		indexes = [models.Index(fields=["county", "name"])]

	def __str__(self) -> str:
		return f"{self.name} ({self.county.name})"


class Constituency(TimeStampedUUIDModel):
	external_id = models.PositiveIntegerField(unique=True, db_index=True)
	subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name="constituencies")
	name = models.CharField(max_length=255)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "constituencies"
		indexes = [models.Index(fields=["subcounty", "name"])]

	def __str__(self) -> str:
		return f"{self.name} ({self.subcounty.name})"


class Ward(TimeStampedUUIDModel):
	external_id = models.PositiveIntegerField(unique=True, db_index=True)
	constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name="wards")
	subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name="wards")
	name = models.CharField(max_length=255)

	class Meta:
		ordering = ["name"]
		indexes = [
			models.Index(fields=["constituency", "name"]),
			models.Index(fields=["subcounty", "name"]),
		]

	def __str__(self) -> str:
		return self.name

	@property
	def ward_code(self) -> str:
		"""Zero-padded station_id for backward-compatible ward_code storage."""
		return str(self.external_id).zfill(4)


class WardProfile(TimeStampedUUIDModel):
	"""Ward-level baseline risk and satellite profile (populated on first registration)."""

	class ProfilingStatus(models.TextChoices):
		PENDING = "pending", "Pending"
		IN_PROGRESS = "in_progress", "In Progress"
		READY = "ready", "Ready"
		FAILED = "failed", "Failed"

	ward = models.OneToOneField(Ward, on_delete=models.CASCADE, related_name="profile")
	status = models.CharField(
		max_length=16,
		choices=ProfilingStatus.choices,
		default=ProfilingStatus.PENDING,
	)
	mean_rainfall_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
	ndvi_baseline = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
	drought_risk_score = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
	flood_risk_score = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
	data_sources = models.JSONField(default=list, blank=True)
	metadata = models.JSONField(default=dict, blank=True)
	profiled_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		indexes = [models.Index(fields=["status"])]

	def __str__(self) -> str:
		return f"Profile({self.ward.name}, {self.status})"


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
