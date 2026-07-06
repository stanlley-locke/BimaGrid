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

	def create(self, request, *args, **kwargs):
		from rest_framework.response import Response
		from rest_framework import status
		from datetime import date, timedelta
		from apps.onboarding.models import FarmerOnboarding
		from apps.pricing.engine import calculate_premium
		from apps.policies.services import issue_policy
		from decimal import Decimal

		data = request.data
		onboarding, _ = FarmerOnboarding.objects.get_or_create(profile=request.user.profile)
		
		crop = data.get("crop", "MAIZE")
		acreage = Decimal(data.get("acreage", "1.0"))
		h3_index = data.get("h3_index", "")

		pricing = calculate_premium(crop, acreage, h3_index, [])
		
		policy_data = {
			"crop": crop,
			"insured_acreage": acreage,
			"coverage_h3": h3_index,
			"premium_amount": pricing["final_premium"],
			"coverage_start": date.today(),
			"coverage_end": date.today() + timedelta(days=180),
		}

		policy = issue_policy(onboarding, policy_data)
		serializer = self.get_serializer(policy)
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	from rest_framework.decorators import action
	from rest_framework.response import Response

	@action(detail=True, methods=["get"])
	def status(self, request, pk=None):
		from rest_framework.response import Response
		policy = self.get_object()
		return Response({"status": policy.status})
