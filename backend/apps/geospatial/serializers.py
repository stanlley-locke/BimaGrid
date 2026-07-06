"""Geospatial serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import Constituency, County, ParcelGeometry, SubCounty, Ward


class CountySerializer(serializers.ModelSerializer):
	class Meta:
		model = County
		fields = ["id", "external_id", "name"]


class SubCountySerializer(serializers.ModelSerializer):
	county_id = serializers.UUIDField(source="county.id", read_only=True)
	county_name = serializers.CharField(source="county.name", read_only=True)

	class Meta:
		model = SubCounty
		fields = ["id", "external_id", "name", "county_id", "county_name"]


class ConstituencySerializer(serializers.ModelSerializer):
	subcounty_id = serializers.UUIDField(source="subcounty.id", read_only=True)
	subcounty_name = serializers.CharField(source="subcounty.name", read_only=True)

	class Meta:
		model = Constituency
		fields = ["id", "external_id", "name", "subcounty_id", "subcounty_name"]


class WardSerializer(serializers.ModelSerializer):
	ward_code = serializers.CharField(read_only=True)
	constituency_id = serializers.UUIDField(source="constituency.id", read_only=True)
	constituency_name = serializers.CharField(source="constituency.name", read_only=True)
	subcounty_id = serializers.UUIDField(source="subcounty.id", read_only=True)
	subcounty_name = serializers.CharField(source="subcounty.name", read_only=True)
	county_name = serializers.CharField(source="subcounty.county.name", read_only=True)

	class Meta:
		model = Ward
		fields = [
			"id",
			"external_id",
			"ward_code",
			"name",
			"constituency_id",
			"constituency_name",
			"subcounty_id",
			"subcounty_name",
			"county_name",
		]


class ParcelGeometrySerializer(serializers.ModelSerializer):
	class Meta:
		model = ParcelGeometry
		fields = ["id", "onboarding", "name", "h3_index", "ward_code", "geometry_geojson", "centroid", "acreage", "source", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]
