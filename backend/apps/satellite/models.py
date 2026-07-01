"""Satellite domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class SatelliteObservation(TimeStampedUUIDModel):
	h3_index = models.CharField(max_length=32, db_index=True)
	scene_id = models.CharField(max_length=128)
	source = models.CharField(max_length=64, default="sentinel-2")
	metric_name = models.CharField(max_length=64)
	metric_value = models.DecimalField(max_digits=12, decimal_places=4)
	observed_at = models.DateTimeField()
	metadata = models.JSONField(default=dict, blank=True)


class SatelliteAnalysis(TimeStampedUUIDModel):
	observation = models.ForeignKey(SatelliteObservation, on_delete=models.CASCADE, related_name="analyses")
	analysis_type = models.CharField(max_length=64)
	result = models.JSONField(default=dict)
	confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
