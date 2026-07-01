"""Pricing URLs."""

from rest_framework.routers import DefaultRouter

from .views import PremiumQuoteViewSet, PricingRuleViewSet


router = DefaultRouter()
router.register(r"pricing-rules", PricingRuleViewSet, basename="pricing-rule")
router.register(r"quotes", PremiumQuoteViewSet, basename="premium-quote")

urlpatterns = router.urls
