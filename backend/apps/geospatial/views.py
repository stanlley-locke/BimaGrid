"""Geospatial API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import ParcelGeometry
from .serializers import ParcelGeometrySerializer


class ParcelGeometryViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ParcelGeometrySerializer

	def get_queryset(self):
		return ParcelGeometry.objects.select_related("onboarding", "onboarding__profile").all()
