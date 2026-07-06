"""Geospatial admin."""

from django.contrib import admin

from .models import Constituency, County, GridRisk, H3Grid, ParcelGeometry, SubCounty, Ward, WardProfile


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
	list_display = ("external_id", "name")
	search_fields = ("name",)


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
	list_display = ("external_id", "name", "county")
	search_fields = ("name", "county__name")
	raw_id_fields = ("county",)


@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
	list_display = ("external_id", "name", "subcounty")
	search_fields = ("name", "subcounty__name")
	raw_id_fields = ("subcounty",)


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
	list_display = ("external_id", "name", "constituency", "subcounty")
	search_fields = ("name", "constituency__name", "subcounty__name")
	raw_id_fields = ("constituency", "subcounty")


@admin.register(WardProfile)
class WardProfileAdmin(admin.ModelAdmin):
	list_display = ("ward", "status", "drought_risk_score", "profiled_at")
	search_fields = ("ward__name",)
	raw_id_fields = ("ward",)


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
