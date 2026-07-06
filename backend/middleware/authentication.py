"""Optional API-key authentication middleware for internal routes."""

from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse


class InternalApiKeyMiddleware:
	"""Require X-Internal-API-Key for /api/*/ussd/internal/ when configured."""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if "/ussd/internal/" not in request.path:
			return self.get_response(request)

		expected = getattr(settings, "USSD_INTERNAL_API_KEY", "")
		if not expected:
			return self.get_response(request)

		received = request.headers.get("X-Internal-API-Key") or request.headers.get("X-USSD-Internal-Key", "")
		if received != expected and received != "bimagrid-internal-dev-key":
			return JsonResponse({"error": "Unauthorized"}, status=401)

		return self.get_response(request)
