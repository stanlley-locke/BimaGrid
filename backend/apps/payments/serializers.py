"""Payments serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import PaymentTransaction, Payout


class PaymentTransactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = PaymentTransaction
		fields = ["id", "policy", "claim", "provider", "reference", "amount", "currency", "status", "provider_payload", "processed_at", "created_at", "updated_at"]
		read_only_fields = ["id", "status", "processed_at", "created_at", "updated_at"]


class PayoutSerializer(serializers.ModelSerializer):
	class Meta:
		model = Payout
		fields = ["id", "policy", "amount", "phone_number", "reference", "status", "tx_hash", "created_at", "updated_at"]
		read_only_fields = ["id", "status", "tx_hash", "created_at", "updated_at"]
