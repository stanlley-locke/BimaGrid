"""Payment API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.queryset import is_admin, scope_policy_queryset

from .models import PaymentTransaction, Payout
from .serializers import PaymentTransactionSerializer, PayoutSerializer
from .webhooks import handle_b2c_result, handle_b2c_timeout, handle_payout_trigger, handle_stk_callback


class PaymentTransactionViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PaymentTransactionSerializer
	filter_backends = [DjangoFilterBackend, OrderingFilter]
	filterset_fields = ["status", "provider"]
	ordering_fields = ["created_at", "amount"]

	def get_queryset(self):
		qs = PaymentTransaction.objects.select_related(
			"policy", "policy__onboarding", "claim"
		)
		if is_admin(self.request.user):
			return qs
		return scope_policy_queryset(qs, self.request.user, via_policy=True)


class PayoutViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = PayoutSerializer
	filter_backends = [DjangoFilterBackend, OrderingFilter]
	filterset_fields = ["status"]
	ordering_fields = ["created_at", "amount"]

	def get_queryset(self):
		qs = Payout.objects.select_related("policy", "policy__onboarding")
		return scope_policy_queryset(qs, self.request.user, via_policy=True)


class MpesaCallbackView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		payment = handle_stk_callback(request.data)
		if payment:
			return Response({"ResultCode": 0, "ResultDesc": "Accepted"})
		return Response({"ResultCode": 1, "ResultDesc": "Unknown checkout"}, status=status.HTTP_404_NOT_FOUND)


class MpesaResultView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		payout = handle_b2c_result(request.data)
		return Response({"ResultCode": 0 if payout else 1})


class MpesaTimeoutView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		handle_b2c_timeout(request.data)
		return Response({"ResultCode": 0})


class PayoutTriggerView(APIView):
	"""Webhook from smart contract: POST /api/payments/payout-trigger/"""

	permission_classes = [permissions.AllowAny]

	def post(self, request):
		result = handle_payout_trigger(request.data)
		return Response(result, status=status.HTTP_202_ACCEPTED)
