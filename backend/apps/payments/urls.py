"""Payment URLs."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
	MpesaCallbackView,
	MpesaResultView,
	MpesaTimeoutView,
	PaymentTransactionViewSet,
	PayoutTriggerView,
	PayoutViewSet,
)


router = DefaultRouter()
router.register(r"payments/payouts", PayoutViewSet, basename="payout")
router.register(r"payments", PaymentTransactionViewSet, basename="payment-transaction")

urlpatterns = [
	path("payments/mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa-callback"),
	path("payments/mpesa/result/", MpesaResultView.as_view(), name="mpesa-result"),
	path("payments/mpesa/timeout/", MpesaTimeoutView.as_view(), name="mpesa-timeout"),
	path("payments/payout-trigger/", PayoutTriggerView.as_view(), name="payout-trigger"),
	*router.urls,
]
