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

	class Meta:
		model = Policy
		fields = [
			"id",
			"onboarding",
			"policy_number",
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
		]
		read_only_fields = ["id", "created_at", "updated_at"]

	def create(self, validated_data):
		return issue_policy(validated_data.pop("onboarding"), validated_data)
