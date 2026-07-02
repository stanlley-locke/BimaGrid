"""Pricing API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.permissions import IsAdminOrReadOnly
from apps.core.queryset import is_admin, scope_profile_queryset

from .models import PremiumQuote, PricingRule
from .serializers import PremiumQuoteSerializer, PricingRuleSerializer


class PricingRuleViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
	serializer_class = PricingRuleSerializer
	queryset = PricingRule.objects.all()
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["crop", "active"]
	search_fields = ["crop"]
	ordering_fields = ["crop", "base_rate_per_acre"]


class PremiumQuoteViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PremiumQuoteSerializer
	filter_backends = [DjangoFilterBackend, OrderingFilter]
	filterset_fields = ["crop"]
	ordering_fields = ["created_at", "final_premium"]

	def get_queryset(self):
		qs = PremiumQuote.objects.select_related("profile")
		if is_admin(self.request.user):
			return qs
		return qs.filter(profile=self.request.user.profile)

	def perform_create(self, serializer):
		serializer.save(profile=self.request.user.profile)
