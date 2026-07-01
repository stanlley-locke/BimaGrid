"""Oracle serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import OracleConsensus, OracleSubmission


class OracleSubmissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = OracleSubmission
		fields = ["id", "oracle_name", "h3_index", "metric_name", "metric_value", "payload", "data_hash", "signature", "consensus_round", "submitted_at"]
		read_only_fields = ["id", "submitted_at"]


class OracleConsensusSerializer(serializers.ModelSerializer):
	class Meta:
		model = OracleConsensus
		fields = ["id", "h3_index", "metric_name", "consensus_value", "round_number", "metadata", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]
