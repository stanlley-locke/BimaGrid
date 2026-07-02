"""Onboarding admin."""

from django.contrib import admin

from .models import FarmerOnboarding, LandParcel


class LandParcelInline(admin.TabularInline):
	model = LandParcel
	extra = 0


@admin.register(FarmerOnboarding)
class FarmerOnboardingAdmin(admin.ModelAdmin):
	list_display = ("profile", "assigned_agent", "ward_code", "crop", "acreage", "verification_level", "status", "submitted_at")
	list_filter = ("crop", "status", "verification_level", "assigned_agent")
	search_fields = ("profile__full_name", "profile__phone_number", "ward_code", "mpesa_number")
	inlines = [LandParcelInline]
	raw_id_fields = ("profile", "assigned_agent")


@admin.register(LandParcel)
class LandParcelAdmin(admin.ModelAdmin):
	list_display = ("onboarding", "name", "ward_code", "h3_index", "acreage", "is_primary", "verified")
	list_filter = ("verified", "is_primary")
	search_fields = ("h3_index", "name", "ward_code")
	raw_id_fields = ("onboarding",)
