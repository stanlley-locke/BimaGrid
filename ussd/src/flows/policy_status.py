"""Check policy status USSD flow."""

from __future__ import annotations

import logging

from src.flows.base import BaseFlow
from src.services.backend_client import BackendAPIError, get_backend_client
from src.screens import backend_error_message, policy_status_message
from src.state.models import UssdSession
from src.utils.phone import normalize_phone

logger = logging.getLogger(__name__)


class PolicyStatusFlow(BaseFlow):
	name = "policy_status"

	def handle(self, session: UssdSession, steps: list[str]) -> str:
		_ = steps
		phone = normalize_phone(session.phone_number)
		client = get_backend_client()
		try:
			result = client.get_policy_status(phone)
		except BackendAPIError:
			logger.exception("Policy status lookup failed for %s", phone)
			return backend_error_message()
		return policy_status_message(result)
