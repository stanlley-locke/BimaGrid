"""Oracle domain models."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedUUIDModel


class OracleSubmission(TimeStampedUUIDModel):
	oracle_name = models.CharField(max_length=64)
	h3_index = models.CharField(max_length=32, db_index=True)
	metric_name = models.CharField(max_length=64)
	metric_value = models.DecimalField(max_digits=12, decimal_places=4)
	payload = models.JSONField(default=dict, blank=True)
	data_hash = models.CharField(max_length=128)
	signature = models.CharField(max_length=256, blank=True)
	consensus_round = models.PositiveIntegerField(default=1)
	submitted_at = models.DateTimeField(auto_now_add=True)


class OracleConsensus(TimeStampedUUIDModel):
	h3_index = models.CharField(max_length=32, db_index=True)
	metric_name = models.CharField(max_length=64)
	consensus_value = models.DecimalField(max_digits=12, decimal_places=4)
	round_number = models.PositiveIntegerField(default=1)
	metadata = models.JSONField(default=dict, blank=True)
