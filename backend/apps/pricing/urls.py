"""Pricing URLs."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PremiumQuoteViewSet, PricingRuleViewSet, quote_view

router = DefaultRouter()
router.register(r"pricing-rules", PricingRuleViewSet, basename="pricing-rule")
router.register(r"quotes", PremiumQuoteViewSet, basename="premium-quote")

urlpatterns = [
    path("pricing/quote/", quote_view, name="pricing-quote"),
] + router.urls
