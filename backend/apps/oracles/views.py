"""Oracle API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import OracleConsensus, OracleSubmission
from .serializers import OracleConsensusSerializer, OracleSubmissionSerializer


class OracleSubmissionViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = OracleSubmissionSerializer
	queryset = OracleSubmission.objects.all()


class OracleConsensusViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = OracleConsensusSerializer
	queryset = OracleConsensus.objects.all()
