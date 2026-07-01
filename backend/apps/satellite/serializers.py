"""Satellite serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import SatelliteAnalysis, SatelliteObservation


class SatelliteObservationSerializer(serializers.ModelSerializer):
	class Meta:
		model = SatelliteObservation
		fields = ["id", "h3_index", "scene_id", "source", "metric_name", "metric_value", "observed_at", "metadata", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class SatelliteAnalysisSerializer(serializers.ModelSerializer):
	class Meta:
		model = SatelliteAnalysis
		fields = ["id", "observation", "analysis_type", "result", "confidence", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]
