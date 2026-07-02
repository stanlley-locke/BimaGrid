"""Claims API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.queryset import scope_policy_queryset

from .models import Claim
from .serializers import ClaimSerializer


class ClaimViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ClaimSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["status", "loss_type"]
	search_fields = ["claim_number", "policy__policy_number"]
	ordering_fields = ["created_at", "claimed_amount"]

	def get_queryset(self):
		qs = Claim.objects.select_related(
			"policy", "policy__onboarding", "policy__onboarding__profile"
		).prefetch_related("reviews")
		return scope_policy_queryset(qs, self.request.user, via_policy=True)
