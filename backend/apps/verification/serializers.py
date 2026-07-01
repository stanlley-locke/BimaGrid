"""Verification serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import VerificationArtifact, VerificationRecord


class VerificationArtifactSerializer(serializers.ModelSerializer):
	class Meta:
		model = VerificationArtifact
		fields = ["id", "artifact_type", "uri", "checksum", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class VerificationRecordSerializer(serializers.ModelSerializer):
	artifacts = VerificationArtifactSerializer(many=True, read_only=True)

	class Meta:
		model = VerificationRecord
		fields = ["id", "onboarding", "verification_type", "status", "findings", "reviewed_by", "reviewed_at", "artifacts", "created_at", "updated_at"]
		read_only_fields = ["id", "reviewed_by", "reviewed_at", "created_at", "updated_at"]
