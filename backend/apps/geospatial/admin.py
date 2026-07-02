"""Geospatial admin."""

from django.contrib import admin

from .models import GridRisk, H3Grid, ParcelGeometry


@admin.register(H3Grid)
class H3GridAdmin(admin.ModelAdmin):
	list_display = ("h3_index", "resolution", "centroid_lat", "centroid_lng", "region_code")
	search_fields = ("h3_index", "region_code")


@admin.register(GridRisk)
class GridRiskAdmin(admin.ModelAdmin):
	list_display = ("h3_index", "mean_rainfall_mm", "drought_risk_score", "flood_risk_score")
	search_fields = ("h3_index",)


@admin.register(ParcelGeometry)
class ParcelGeometryAdmin(admin.ModelAdmin):
	list_display = ("onboarding", "name", "h3_index", "ward_code", "acreage", "source")
	raw_id_fields = ("onboarding",)
