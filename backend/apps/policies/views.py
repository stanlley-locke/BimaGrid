"""Policy API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Policy
from .serializers import PolicySerializer


class PolicyViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PolicySerializer

	def get_queryset(self):
		return Policy.objects.select_related("onboarding", "onboarding__profile").prefetch_related("events").all()
