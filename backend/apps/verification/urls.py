"""Verification URLs."""

from rest_framework.routers import DefaultRouter

from .views import VerificationArtifactViewSet, VerificationRecordViewSet


router = DefaultRouter()
router.register(r"verification-records", VerificationRecordViewSet, basename="verification-record")
router.register(r"verification-artifacts", VerificationArtifactViewSet, basename="verification-artifact")

urlpatterns = router.urls
