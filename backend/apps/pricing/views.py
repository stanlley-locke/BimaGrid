"""Pricing API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import PremiumQuote, PricingRule
from .serializers import PremiumQuoteSerializer, PricingRuleSerializer


class PricingRuleViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PricingRuleSerializer
	queryset = PricingRule.objects.all()


class PremiumQuoteViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PremiumQuoteSerializer

	def get_queryset(self):
		return PremiumQuote.objects.select_related("profile").all()

	def perform_create(self, serializer):
		serializer.save(profile=self.request.user.profile)
