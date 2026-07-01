"""Verification admin."""

from django.contrib import admin

from .models import VerificationArtifact, VerificationRecord


class VerificationArtifactInline(admin.TabularInline):
	model = VerificationArtifact
	extra = 0


@admin.register(VerificationRecord)
class VerificationRecordAdmin(admin.ModelAdmin):
	list_display = ("onboarding", "verification_type", "status", "reviewed_by", "reviewed_at")
	raw_id_fields = ("onboarding", "reviewed_by")
	inlines = [VerificationArtifactInline]


@admin.register(VerificationArtifact)
class VerificationArtifactAdmin(admin.ModelAdmin):
	list_display = ("record", "artifact_type", "uri")
	raw_id_fields = ("record",)
