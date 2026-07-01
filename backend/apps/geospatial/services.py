"""Geospatial services."""

from __future__ import annotations

from .models import ParcelGeometry


def register_parcel_geometry(onboarding, geometry_data: dict) -> ParcelGeometry:
	return ParcelGeometry.objects.create(onboarding=onboarding, **geometry_data)
