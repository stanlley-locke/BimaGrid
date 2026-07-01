"""Policy admin."""

from django.contrib import admin

from .models import Policy, PolicyEvent


class PolicyEventInline(admin.TabularInline):
	model = PolicyEvent
	extra = 0


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
	list_display = ("policy_number", "crop", "insured_acreage", "coverage_h3", "premium_amount", "status", "coverage_start", "coverage_end")
	list_filter = ("crop", "status")
	search_fields = ("policy_number", "coverage_h3", "onboarding__profile__full_name")
	raw_id_fields = ("onboarding",)
	inlines = [PolicyEventInline]


@admin.register(PolicyEvent)
class PolicyEventAdmin(admin.ModelAdmin):
	list_display = ("policy", "event_type", "created_at")
	raw_id_fields = ("policy",)
