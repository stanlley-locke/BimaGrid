"""Verification API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import VerificationArtifact, VerificationRecord
from .serializers import VerificationArtifactSerializer, VerificationRecordSerializer


class VerificationRecordViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = VerificationRecordSerializer
	queryset = VerificationRecord.objects.select_related("onboarding", "reviewed_by").prefetch_related("artifacts")


class VerificationArtifactViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = VerificationArtifactSerializer
	queryset = VerificationArtifact.objects.select_related("record").all()
