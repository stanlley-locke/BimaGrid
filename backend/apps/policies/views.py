"""Policy API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.queryset import scope_policy_queryset

from .models import Policy
from .serializers import PolicySerializer


class PolicyViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PolicySerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["status", "crop", "coverage_h3"]
	search_fields = ["policy_number", "coverage_h3"]
	ordering_fields = ["created_at", "coverage_start", "premium_amount"]

	def get_queryset(self):
		qs = Policy.objects.select_related(
			"onboarding", "onboarding__profile", "onboarding__assigned_agent"
		).prefetch_related("events")
		return scope_policy_queryset(qs, self.request.user)
