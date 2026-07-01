"""Satellite URLs."""

from rest_framework.routers import DefaultRouter

from .views import SatelliteAnalysisViewSet, SatelliteObservationViewSet


router = DefaultRouter()
router.register(r"satellite-observations", SatelliteObservationViewSet, basename="satellite-observation")
router.register(r"satellite-analyses", SatelliteAnalysisViewSet, basename="satellite-analysis")

urlpatterns = router.urls
