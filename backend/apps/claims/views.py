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

	def create(self, request, *args, **kwargs):
		from rest_framework.response import Response
		from rest_framework import status
		from apps.core.utils import build_reference_code
		from apps.policies.models import Policy
		from decimal import Decimal

		data = request.data
		policy_id = data.get("policy_id")
		
		try:
			policy = Policy.objects.get(id=policy_id)
		except Policy.DoesNotExist:
			return Response({"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)

		amount = Decimal(data.get("estimated_loss_kes", "0"))
		claim = Claim.objects.create(
			policy=policy,
			claim_number=build_reference_code("CLM"),
			loss_type=data.get("loss_type", "unknown"),
			description=data.get("description", ""),
			claimed_amount=amount,
			status=Claim.Status.SUBMITTED
		)

		serializer = self.get_serializer(claim)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
