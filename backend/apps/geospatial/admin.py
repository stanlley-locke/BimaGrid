"""Geospatial admin."""

from django.contrib import admin

from .models import ParcelGeometry


@admin.register(ParcelGeometry)
class ParcelGeometryAdmin(admin.ModelAdmin):
	list_display = ("onboarding", "name", "h3_index", "ward_code", "acreage", "source")
	raw_id_fields = ("onboarding",)
