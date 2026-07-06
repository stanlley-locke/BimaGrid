"""Geospatial URLs."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .geography_views import (
	CountyListView,
	CountySubCountyListView,
	SubCountyConstituencyListView,
	WardListView,
)
from .views import ParcelGeometryViewSet, h3_index_view


router = DefaultRouter()
router.register(r"geospatial/parcels", ParcelGeometryViewSet, basename="parcel-geometry")

urlpatterns = [
	path("geography/counties/", CountyListView.as_view(), name="geography-counties"),
	path(
		"geography/counties/<uuid:county_id>/subcounties/",
		CountySubCountyListView.as_view(),
		name="geography-county-subcounties",
	),
	path(
		"geography/subcounties/<uuid:subcounty_id>/constituencies/",
		SubCountyConstituencyListView.as_view(),
		name="geography-subcounty-constituencies",
	),
	path("geography/wards/", WardListView.as_view(), name="geography-wards"),
	path("geospatial/h3-index/", h3_index_view, name="geospatial-h3-index"),
] + router.urls
