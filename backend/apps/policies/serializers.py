"""Policy serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import Policy, PolicyEvent
from .services import issue_policy


class PolicyEventSerializer(serializers.ModelSerializer):
	class Meta:
		model = PolicyEvent
		fields = ["id", "event_type", "details", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class PolicySerializer(serializers.ModelSerializer):
	events = PolicyEventSerializer(many=True, read_only=True)
	farmer_name = serializers.CharField(source="onboarding.profile.full_name", read_only=True)
	farmer_phone = serializers.CharField(source="onboarding.profile.phone_number", read_only=True)
	ward_name = serializers.CharField(source="onboarding.ward.name", read_only=True, default=None)
	constituency_name = serializers.CharField(source="onboarding.ward.constituency.name", read_only=True, default=None)
	subcounty_name = serializers.CharField(source="onboarding.ward.subcounty.name", read_only=True, default=None)
	county_name = serializers.CharField(source="onboarding.ward.subcounty.county.name", read_only=True, default=None)

	class Meta:
		model = Policy
		fields = [
			"id",
			"onboarding",
			"policy_number",
			"farmer_name",
			"farmer_phone",
			"crop",
			"insured_acreage",
			"coverage_h3",
			"premium_amount",
			"coverage_start",
			"coverage_end",
			"mitigation_discount_percent",
			"status",
			"metadata",
			"events",
			"created_at",
			"updated_at",
			"ward_name",
			"constituency_name",
			"subcounty_name",
			"county_name",
		]
		read_only_fields = ["id", "created_at", "updated_at"]

	def create(self, validated_data):
		return issue_policy(validated_data.pop("onboarding"), validated_data)
