"""Pricing admin."""

from django.contrib import admin

from .models import PremiumQuote, PricingRule


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
	list_display = ("crop", "base_rate_per_acre", "drought_multiplier", "flood_multiplier", "mitigation_discount_cap", "active")
	list_filter = ("active",)
	search_fields = ("crop",)


@admin.register(PremiumQuote)
class PremiumQuoteAdmin(admin.ModelAdmin):
	list_display = ("profile", "crop", "acreage", "base_premium", "discount_amount", "final_premium")
	raw_id_fields = ("profile",)
