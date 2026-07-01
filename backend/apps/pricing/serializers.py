"""Pricing serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import PremiumQuote, PricingRule
from .services import calculate_quote


class PricingRuleSerializer(serializers.ModelSerializer):
	class Meta:
		model = PricingRule
		fields = ["id", "crop", "base_rate_per_acre", "drought_multiplier", "flood_multiplier", "mitigation_discount_cap", "active", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class PremiumQuoteSerializer(serializers.ModelSerializer):
	class Meta:
		model = PremiumQuote
		fields = ["id", "profile", "crop", "acreage", "base_premium", "discount_amount", "final_premium", "risk_metadata", "created_at", "updated_at"]
		read_only_fields = ["id", "base_premium", "discount_amount", "final_premium", "created_at", "updated_at"]

	def create(self, validated_data):
		profile = validated_data.pop("profile")
		return calculate_quote(profile, validated_data)
