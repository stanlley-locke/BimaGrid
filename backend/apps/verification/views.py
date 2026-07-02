"""Verification API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.queryset import scope_onboarding_queryset

from .models import VerificationArtifact, VerificationRecord
from .serializers import VerificationArtifactSerializer, VerificationRecordSerializer


class VerificationRecordViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = VerificationRecordSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["status", "verification_type"]
	search_fields = ["onboarding__profile__full_name"]
	ordering_fields = ["created_at"]

	def get_queryset(self):
		qs = VerificationRecord.objects.select_related(
			"onboarding", "onboarding__profile", "reviewed_by"
		).prefetch_related("artifacts")
		return scope_onboarding_queryset(qs, self.request.user, prefix="onboarding__")


class VerificationArtifactViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = VerificationArtifactSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter]
	filterset_fields = ["artifact_type"]
	search_fields = ["uri"]

	def get_queryset(self):
		qs = VerificationArtifact.objects.select_related(
			"record", "record__onboarding", "record__onboarding__profile"
		)
		return scope_onboarding_queryset(qs, self.request.user, prefix="record__onboarding__")
