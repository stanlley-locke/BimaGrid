"""USSD gateway HTTP views."""

from __future__ import annotations

import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from src.flows.dispatcher import handle_ussd_session
from src.gateway.serializers import parse_ussd_request, validate_ussd_request
from src.integrations.africastalking import verify_africastalking_signature
from src.screens import end

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class UssdGatewayView(View):
	"""POST /ussd/gateway/ — Africa's Talking USSD webhook handler."""

	def post(self, request, *args, **kwargs):
		payload = request.POST.dict()
		ussd_request = parse_ussd_request(payload)
		valid, error = validate_ussd_request(ussd_request)
		if not valid:
			return HttpResponseBadRequest(error)

		headers = {key: value for key, value in request.headers.items()}
		if not verify_africastalking_signature(
			headers,
			username=ussd_request.service_code or "",
			session_id=ussd_request.session_id,
			phone_number=ussd_request.phone_number,
			text=ussd_request.text,
			service_code=ussd_request.service_code,
		):
			logger.warning("Rejected USSD request with invalid signature: %s", ussd_request.session_id)
			return HttpResponse(end("Unauthorized request."), content_type="text/plain", status=403)

		try:
			response_text = handle_ussd_session(
				ussd_request.session_id,
				ussd_request.phone_number,
				ussd_request.text,
			)
		except Exception:
			logger.exception("Unhandled USSD error for session %s", ussd_request.session_id)
			response_text = end("Service error. Please try again later.")

		return HttpResponse(response_text, content_type="text/plain")

	def get(self, request, *args, **kwargs):
		return HttpResponse(
			end("Use POST for USSD gateway callbacks."),
			content_type="text/plain",
			status=405,
		)
