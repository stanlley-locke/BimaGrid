"""Geospatial API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.queryset import scope_onboarding_queryset

from .models import ParcelGeometry
from .serializers import ParcelGeometrySerializer


class ParcelGeometryViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ParcelGeometrySerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["h3_index", "ward_code", "source"]
	search_fields = ["name", "h3_index", "ward_code"]
	ordering_fields = ["created_at", "acreage"]

	def get_queryset(self):
		qs = ParcelGeometry.objects.select_related(
			"onboarding", "onboarding__profile", "onboarding__assigned_agent"
		)
		return scope_onboarding_queryset(qs, self.request.user)
