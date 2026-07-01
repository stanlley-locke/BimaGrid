"""Satellite admin."""

from django.contrib import admin

from .models import SatelliteAnalysis, SatelliteObservation


@admin.register(SatelliteObservation)
class SatelliteObservationAdmin(admin.ModelAdmin):
	list_display = ("h3_index", "scene_id", "source", "metric_name", "metric_value", "observed_at")


@admin.register(SatelliteAnalysis)
class SatelliteAnalysisAdmin(admin.ModelAdmin):
	list_display = ("observation", "analysis_type", "confidence", "created_at")
	raw_id_fields = ("observation",)
