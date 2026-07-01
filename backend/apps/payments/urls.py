"""Payment URLs."""

from rest_framework.routers import DefaultRouter

from .views import PaymentTransactionViewSet, PayoutViewSet


router = DefaultRouter()
router.register(r"payments", PaymentTransactionViewSet, basename="payment-transaction")
router.register(r"payouts", PayoutViewSet, basename="payout")

urlpatterns = router.urls
