"""USSD gateway HTTP endpoint for Africa's Talking."""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from .services import handle_ussd_session

logger = logging.getLogger(__name__)


def _proxy_to_standalone_service(request) -> HttpResponse | None:
	"""Forward USSD webhook to standalone service when USSD_SERVICE_URL is configured."""
	service_url = getattr(settings, "USSD_SERVICE_URL", "").rstrip("/")
	if not service_url:
		return None

	payload = {
		"sessionId": request.data.get("sessionId") or request.POST.get("sessionId", ""),
		"phoneNumber": request.data.get("phoneNumber") or request.POST.get("phoneNumber", ""),
		"text": request.data.get("text") or request.POST.get("text", ""),
		"serviceCode": request.data.get("serviceCode") or request.POST.get("serviceCode", ""),
		"networkCode": request.data.get("networkCode") or request.POST.get("networkCode", ""),
	}
	timeout = getattr(settings, "USSD_SERVICE_TIMEOUT", 10.0)

	try:
		response = requests.post(
			f"{service_url}/ussd/gateway/",
			data=payload,
			timeout=timeout,
		)
	except requests.RequestException:
		logger.exception("Failed to proxy USSD request to %s", service_url)
		return HttpResponse(
			"END Service temporarily unavailable. Please try again.",
			content_type="text/plain",
			status=503,
		)

	return HttpResponse(response.text, content_type="text/plain", status=response.status_code)


@method_decorator(csrf_exempt, name="dispatch")
class UssdGatewayView(APIView):
	"""POST /ussd/gateway/ — Africa's Talking USSD webhook."""

	authentication_classes = []
	permission_classes = []

	def post(self, request):
		proxied = _proxy_to_standalone_service(request)
		if proxied is not None:
			return proxied

		session_id = request.data.get("sessionId") or request.POST.get("sessionId", "")
		phone = request.data.get("phoneNumber") or request.POST.get("phoneNumber", "")
		text = request.data.get("text") or request.POST.get("text", "")
		response_text = handle_ussd_session(session_id, phone, text)
		return HttpResponse(response_text, content_type="text/plain")
