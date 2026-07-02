"""Africa's Talking webhook signature verification."""

from __future__ import annotations

import hashlib
import hmac
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def build_signature_payload(
	username: str,
	session_id: str,
	phone_number: str,
	text: str,
	service_code: str = "",
) -> str:
	"""Build the canonical string used for Africa's Talking USSD signature checks."""
	parts = [username, session_id, phone_number, text]
	if service_code:
		parts.append(service_code)
	return "|".join(parts)


def compute_signature(payload: str, api_key: str) -> str:
	digest = hmac.new(api_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
	return digest


def verify_africastalking_signature(
	request_headers: dict[str, str],
	*,
	username: str,
	session_id: str,
	phone_number: str,
	text: str,
	service_code: str = "",
) -> bool:
	"""Verify Africa's Talking webhook signature when verification is enabled."""
	if not settings.AFRICASTALKING_VERIFY_SIGNATURE:
		return True

	api_key = settings.AFRICASTALKING_API_KEY
	if not api_key:
		logger.warning("Signature verification enabled but AFRICASTALKING_API_KEY is empty")
		return False

	received = (
		request_headers.get("X-AT-Signature")
		or request_headers.get("X-AfricasTalking-Signature")
		or request_headers.get("HTTP_X_AT_SIGNATURE")
		or ""
	)
	if not received:
		logger.warning("Missing Africa's Talking signature header")
		return False

	payload = build_signature_payload(username, session_id, phone_number, text, service_code)
	expected = compute_signature(payload, api_key)
	valid = hmac.compare_digest(received.lower(), expected.lower())
	if not valid:
		logger.warning("Invalid Africa's Talking signature for session %s", session_id)
	return valid
