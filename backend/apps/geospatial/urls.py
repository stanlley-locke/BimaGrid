"""Geospatial URLs."""

from rest_framework.routers import DefaultRouter

from .views import ParcelGeometryViewSet


router = DefaultRouter()
router.register(r"geospatial/parcels", ParcelGeometryViewSet, basename="parcel-geometry")

urlpatterns = router.urls
