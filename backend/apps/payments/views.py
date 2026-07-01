"""Payment API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import PaymentTransaction, Payout
from .serializers import PaymentTransactionSerializer, PayoutSerializer


class PaymentTransactionViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PaymentTransactionSerializer

	def get_queryset(self):
		return PaymentTransaction.objects.select_related("policy", "claim").all()


class PayoutViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PayoutSerializer
	queryset = Payout.objects.select_related("policy").all()
