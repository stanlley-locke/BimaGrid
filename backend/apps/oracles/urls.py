"""Oracle URLs."""

from rest_framework.routers import DefaultRouter

from .views import OracleConsensusViewSet, OracleSubmissionViewSet


router = DefaultRouter()
router.register(r"oracle-submissions", OracleSubmissionViewSet, basename="oracle-submission")
router.register(r"oracle-consensus", OracleConsensusViewSet, basename="oracle-consensus")

urlpatterns = router.urls
