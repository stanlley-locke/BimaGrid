"""Onboarding serializers."""

from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from .constants import CropChoice, OnboardingStatus
from .models import FarmerOnboarding, LandParcel
from .services import get_or_create_onboarding, refresh_onboarding_level, replace_land_parcels
from .validators import validate_geojson_geometry, validate_mpesa_number, validate_positive_acreage


class LandParcelSerializer(serializers.ModelSerializer):
	class Meta:
		model = LandParcel
		fields = [
			"id",
			"name",
			"ward_code",
			"h3_index",
			"geometry_geojson",
			"ownership_docs",
			"acreage",
			"is_primary",
			"verified",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "verified", "created_at", "updated_at"]

	def validate_geometry_geojson(self, value):
		validate_geojson_geometry(value)
		return value

	def validate_acreage(self, value):
		validate_positive_acreage(value)
		return value


class FarmerOnboardingSerializer(serializers.ModelSerializer):
	land_parcels = LandParcelSerializer(many=True, required=False)
	stage_label = serializers.CharField(read_only=True)

	class Meta:
		model = FarmerOnboarding
		fields = [
			"id",
			"profile",
			"ward_code",
			"crop",
			"acreage",
			"mpesa_number",
			"verification_level",
			"stage_label",
			"status",
			"notes",
			"submitted_at",
			"approved_at",
			"rejection_reason",
			"land_parcels",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "profile", "verification_level", "submitted_at", "approved_at", "created_at", "updated_at"]

	def validate_crop(self, value):
		if value and value not in CropChoice.values:
			raise serializers.ValidationError("Select a valid crop.")
		return value

	def validate_mpesa_number(self, value):
		if value:
			validate_mpesa_number(value)
		return value

	def validate_status(self, value):
		if value and value not in OnboardingStatus.values:
			raise serializers.ValidationError("Select a valid status.")
		return value

	def validate(self, attrs):
		acreage = attrs.get("acreage")
		if acreage is not None:
			validate_positive_acreage(acreage)
		return attrs

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation["stage_label"] = instance.stage_label()
		return representation

	@transaction.atomic
	def create(self, validated_data):
		parcels_data = validated_data.pop("land_parcels", [])
		profile = self.context["profile"]
		onboarding = get_or_create_onboarding(profile)
		for attr, value in validated_data.items():
			setattr(onboarding, attr, value)
		onboarding.save()
		replace_land_parcels(onboarding, parcels_data)
		refresh_onboarding_level(onboarding)
		return onboarding

	@transaction.atomic
	def update(self, instance, validated_data):
		parcels_data = validated_data.pop("land_parcels", None)
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		if parcels_data is not None:
			replace_land_parcels(instance, parcels_data)
		refresh_onboarding_level(instance)
		return instance
