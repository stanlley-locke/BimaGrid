"""Satellite API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import SatelliteAnalysis, SatelliteObservation
from .serializers import SatelliteAnalysisSerializer, SatelliteObservationSerializer


class SatelliteObservationViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = SatelliteObservationSerializer
	queryset = SatelliteObservation.objects.all()


class SatelliteAnalysisViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = SatelliteAnalysisSerializer
	queryset = SatelliteAnalysis.objects.select_related("observation").all()
