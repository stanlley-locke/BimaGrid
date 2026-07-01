"""Geospatial serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import ParcelGeometry


class ParcelGeometrySerializer(serializers.ModelSerializer):
	class Meta:
		model = ParcelGeometry
		fields = ["id", "onboarding", "name", "h3_index", "ward_code", "geometry_geojson", "centroid", "acreage", "source", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]
