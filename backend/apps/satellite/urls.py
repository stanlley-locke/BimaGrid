"""Satellite URLs."""

from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import SatelliteAnalysisViewSet, SatelliteObservationViewSet, rainfall_view, ndvi_view

router = DefaultRouter()
router.register(r"satellite-observations", SatelliteObservationViewSet, basename="satellite-observation")
router.register(r"satellite-analyses", SatelliteAnalysisViewSet, basename="satellite-analysis")

urlpatterns = [
	path("satellite/rainfall/", rainfall_view, name="satellite-rainfall"),
	path("satellite/ndvi/", ndvi_view, name="satellite-ndvi"),
	*router.urls,
]
