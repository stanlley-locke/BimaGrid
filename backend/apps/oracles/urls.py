"""Oracle URLs."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OracleConsensusViewSet, OracleSubmitDataView, OracleSubmissionViewSet


router = DefaultRouter()
router.register(r"oracle-submissions", OracleSubmissionViewSet, basename="oracle-submission")
router.register(r"oracle-consensus", OracleConsensusViewSet, basename="oracle-consensus")

urlpatterns = [
	path("oracles/submit-data/", OracleSubmitDataView.as_view(), name="oracle-submit-data"),
	path("oracles/", OracleSubmissionViewSet.as_view({"get": "list"}), name="oracles-list"),
	*router.urls,
]
