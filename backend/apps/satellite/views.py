"""Satellite API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.permissions import IsBrokerOrAdmin
from apps.core.queryset import is_admin, scope_h3_queryset

from .models import SatelliteAnalysis, SatelliteObservation
from .serializers import SatelliteAnalysisSerializer, SatelliteObservationSerializer


class SatelliteObservationViewSet(viewsets.ReadOnlyModelViewSet):
	permission_classes = [permissions.IsAuthenticated, IsBrokerOrAdmin]
	serializer_class = SatelliteObservationSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["h3_index", "source", "metric_name"]
	search_fields = ["h3_index", "scene_id"]
	ordering_fields = ["observed_at"]

	def get_queryset(self):
		qs = SatelliteObservation.objects.all()
		if is_admin(self.request.user):
			return qs
		return scope_h3_queryset(qs, self.request.user)


class SatelliteAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
	permission_classes = [permissions.IsAuthenticated, IsBrokerOrAdmin]
	serializer_class = SatelliteAnalysisSerializer
	filter_backends = [DjangoFilterBackend, OrderingFilter]
	filterset_fields = ["analysis_type"]
	ordering_fields = ["created_at"]

	def get_queryset(self):
		qs = SatelliteAnalysis.objects.select_related("observation")
		if is_admin(self.request.user):
			return qs
		h3_scoped = scope_h3_queryset(
			SatelliteObservation.objects.all(), self.request.user
		).values_list("id", flat=True)
		return qs.filter(observation_id__in=h3_scoped)
