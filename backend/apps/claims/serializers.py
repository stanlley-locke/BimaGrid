"""Claims serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import Claim, ClaimReview
from .services import open_claim


class ClaimReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = ClaimReview
		fields = ["id", "reviewed_by", "decision", "notes", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class ClaimSerializer(serializers.ModelSerializer):
	reviews = ClaimReviewSerializer(many=True, read_only=True)

	class Meta:
		model = Claim
		fields = [
			"id",
			"policy",
			"claim_number",
			"loss_type",
			"description",
			"claimed_amount",
			"trigger_value",
			"threshold_value",
			"evidence",
			"status",
			"reviews",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "created_at", "updated_at"]

	def create(self, validated_data):
		policy = validated_data.pop("policy")
		return open_claim(policy, validated_data)
