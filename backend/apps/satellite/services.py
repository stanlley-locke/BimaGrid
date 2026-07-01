"""Satellite services."""

from __future__ import annotations

from .models import SatelliteAnalysis, SatelliteObservation


def record_observation(observation_data: dict) -> SatelliteObservation:
	return SatelliteObservation.objects.create(**observation_data)


def store_analysis(observation: SatelliteObservation, analysis_data: dict) -> SatelliteAnalysis:
	return SatelliteAnalysis.objects.create(observation=observation, **analysis_data)
