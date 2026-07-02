"""Oracle API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsBrokerOrAdmin
from apps.core.queryset import is_admin, scope_h3_queryset

from .models import OracleConsensus, OracleSubmission
from .serializers import OracleConsensusSerializer, OracleSubmissionSerializer
from .services import ingest_oracle_payload


class OracleSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
	permission_classes = [permissions.IsAuthenticated, IsBrokerOrAdmin]
	serializer_class = OracleSubmissionSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["h3_index", "metric_name", "oracle_name", "consensus_round"]
	search_fields = ["h3_index", "oracle_name"]
	ordering_fields = ["submitted_at", "metric_value"]

	def get_queryset(self):
		qs = OracleSubmission.objects.all()
		if is_admin(self.request.user):
			return qs
		return scope_h3_queryset(qs, self.request.user)


class OracleConsensusViewSet(viewsets.ReadOnlyModelViewSet):
	permission_classes = [permissions.IsAuthenticated, IsBrokerOrAdmin]
	serializer_class = OracleConsensusSerializer
	filter_backends = [DjangoFilterBackend, OrderingFilter]
	filterset_fields = ["h3_index", "metric_name", "round_number"]
	ordering_fields = ["created_at", "consensus_value"]

	def get_queryset(self):
		qs = OracleConsensus.objects.all()
		if is_admin(self.request.user):
			return qs
		return scope_h3_queryset(qs, self.request.user)


class OracleSubmitDataView(APIView):
	"""Internal endpoint for oracle nodes: POST /api/oracles/submit-data/"""

	permission_classes = [permissions.AllowAny]

	def post(self, request):
		signature = request.headers.get("X-Oracle-Signature", "")
		payload = request.data
		required = {"oracle_id", "h3_index", "timestamp"}
		if not required.issubset(payload.keys()):
			return Response(
				{"error": f"Missing fields: {sorted(required - payload.keys())}"},
				status=status.HTTP_400_BAD_REQUEST,
			)
		normalized = {
			"oracle_id": payload["oracle_id"],
			"h3_index": payload["h3_index"],
			"timestamp": payload["timestamp"],
			"rainfall_mm": payload.get("rainfall_mm", 0),
			"ndvi": payload.get("ndvi", 0),
			"soil_moisture": payload.get("soil_moisture", 0),
			"data_sources": payload.get("data_sources", []),
		}
		result = ingest_oracle_payload(normalized, signature)
		return Response(result, status=status.HTTP_201_CREATED)
