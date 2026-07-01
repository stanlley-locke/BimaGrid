"""Oracle admin."""

from django.contrib import admin

from .models import OracleConsensus, OracleSubmission


@admin.register(OracleSubmission)
class OracleSubmissionAdmin(admin.ModelAdmin):
	list_display = ("oracle_name", "h3_index", "metric_name", "metric_value", "consensus_round", "submitted_at")
	search_fields = ("oracle_name", "h3_index", "data_hash")


@admin.register(OracleConsensus)
class OracleConsensusAdmin(admin.ModelAdmin):
	list_display = ("h3_index", "metric_name", "consensus_value", "round_number", "created_at")
