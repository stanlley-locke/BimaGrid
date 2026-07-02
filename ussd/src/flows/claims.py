"""File claim USSD flow (parametric insurance)."""

from __future__ import annotations

import logging

from src.flows.base import BaseFlow
from src.services.backend_client import BackendAPIError, get_backend_client
from src.screens import backend_error_message, claim_message
from src.state.models import UssdSession
from src.utils.phone import normalize_phone

logger = logging.getLogger(__name__)


class ClaimsFlow(BaseFlow):
	name = "claims"

	def handle(self, session: UssdSession, steps: list[str]) -> str:
		phone = normalize_phone(session.phone_number)
		flow_steps = steps[1:]

		if len(flow_steps) == 0:
			return self.continue_response(
				"BimaGrid uses parametric claims.\n"
				"1. Check automatic claim status\n"
				"2. Learn about parametric payouts"
			)

		choice = flow_steps[0]
		client = get_backend_client()

		if choice == "1":
			try:
				result = client.file_claim(phone, loss_type="drought", description="USSD status check")
			except BackendAPIError:
				logger.exception("Claim status lookup failed for %s", phone)
				return backend_error_message()
			return claim_message(result)

		if choice == "2":
			return self.end_response(
				"Parametric claims trigger automatically when satellite "
				"data confirms drought in your H3 grid. No manual filing needed."
			)

		return self.end_response("Invalid option. Dial again to restart.")
