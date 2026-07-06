"""Admin dashboard God Mode API views."""

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminUser
from apps.oracles.services import simulate_drought_data
from apps.oracles.tasks import evaluate_h3_hexagon
from apps.payments.services import bypass_payment_for_policy
from apps.policies.models import Policy


class GodModeDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
	"""HTML demo dashboard for God Mode admin actions."""

	template_name = "admin_dashboard/god_mode.html"

	def test_func(self) -> bool:
		user = self.request.user
		if not user.is_authenticated:
			return False
		if user.is_staff:
			return True
		profile = getattr(user, "profile", None)
		return getattr(profile, "role", "") == "admin"


class SimulateDroughtView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAdminUser]

	def post(self, request):
		h3_index = request.data.get("h3_index")
		rainfall_mm = float(request.data.get("rainfall_mm", 15.0))
		ndvi = float(request.data.get("ndvi", 0.35))
		if not h3_index:
			return Response({"error": "h3_index is required"}, status=status.HTTP_400_BAD_REQUEST)
		result = simulate_drought_data(h3_index, rainfall_mm, ndvi)
		return Response(result, status=status.HTTP_200_OK)


class TriggerEvaluationView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAdminUser]

	def post(self, request):
		h3_index = request.data.get("h3_index")
		simulate_drought = bool(request.data.get("simulate_drought", False))
		if not h3_index:
			return Response({"error": "h3_index is required"}, status=status.HTTP_400_BAD_REQUEST)
		task = evaluate_h3_hexagon.delay(h3_index, simulate_drought=simulate_drought)
		return Response({"task_id": task.id, "h3_index": h3_index, "status": "queued"}, status=status.HTTP_202_ACCEPTED)


class BypassPaymentView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAdminUser]

	def post(self, request):
		policy_id = request.data.get("policy_id")
		if not policy_id:
			return Response({"error": "policy_id is required"}, status=status.HTTP_400_BAD_REQUEST)
		policy = Policy.objects.filter(policy_number=policy_id).first()
		if not policy:
			return Response({"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)
		payment = bypass_payment_for_policy(policy)
		return Response(
			{
				"policy_id": policy.policy_number,
				"status": policy.status,
				"payment_reference": payment.reference,
			},
			status=status.HTTP_200_OK,
		)


class AdminStatsView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAdminUser]

	def get(self, request):
		return Response(
			{
				"total_policies": Policy.objects.count(),
				"total_payouts": 0,
			},
			status=status.HTTP_200_OK,
		)
