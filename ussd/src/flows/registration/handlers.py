"""Farmer registration USSD flow."""

from __future__ import annotations

import logging

from src.flows.base import BaseFlow
from src.flows.registration import screens
from src.flows.registration.validators import (
	validate_acreage,
	validate_crop_choice,
	validate_mpesa_choice,
	validate_ward_code,
)
from src.services.backend_client import BackendAPIError, get_backend_client
from src.screens import backend_error_message, session_expired
from src.state.models import UssdSession
from src.utils.phone import normalize_phone

logger = logging.getLogger(__name__)


class RegistrationFlow(BaseFlow):
	name = "registration"

	def handle(self, session: UssdSession, steps: list[str]) -> str:
		phone = normalize_phone(session.phone_number)
		# steps include main menu choice "1" at index 0
		flow_steps = steps[1:]

		if len(flow_steps) == 0:
			return screens.ward_code_prompt()

		if len(flow_steps) == 1:
			valid, _ward = validate_ward_code(flow_steps[0])
			if not valid:
				return screens.invalid_ward_code_prompt()
			return screens.crop_selection_prompt()

		if len(flow_steps) == 2:
			valid, _crop_code, _crop_label = validate_crop_choice(flow_steps[1])
			if not valid:
				return screens.invalid_crop_prompt()
			return screens.acreage_prompt()

		if len(flow_steps) == 3:
			valid, _acreage = validate_acreage(flow_steps[2])
			if not valid or _acreage is None:
				return screens.invalid_acreage_prompt()
			return screens.mpesa_confirm_prompt(phone)

		if len(flow_steps) == 4:
			mpesa_choice = flow_steps[3]
			valid, mpesa = validate_mpesa_choice(mpesa_choice, phone)
			if not valid:
				if mpesa_choice == "2":
					return self.continue_response("Enter M-Pesa number (254XXXXXXXXX):")
				return screens.invalid_mpesa_prompt()
			return self._submit_registration(phone, flow_steps, mpesa)

		if len(flow_steps) == 5 and flow_steps[3] == "2":
			valid, mpesa = validate_mpesa_choice("2", phone, flow_steps[4])
			if not valid:
				return screens.invalid_mpesa_prompt()
			return self._submit_registration(phone, flow_steps, mpesa)

		return session_expired()

	def _submit_registration(self, phone: str, flow_steps: list[str], mpesa: str) -> str:
		valid, ward_code = validate_ward_code(flow_steps[0])
		if not valid:
			return screens.invalid_ward_code_prompt()
		valid, crop_code, crop_label = validate_crop_choice(flow_steps[1])
		if not valid:
			return screens.invalid_crop_prompt()
		valid, acreage = validate_acreage(flow_steps[2])
		if not valid or acreage is None:
			return screens.invalid_acreage_prompt()

		client = get_backend_client()
		try:
			result = client.register_farmer(
				phone=phone,
				ward_code=ward_code,
				crop=crop_code,
				acreage=str(acreage),
				mpesa_number=mpesa,
			)
		except BackendAPIError:
			logger.exception("Registration backend call failed for %s", phone)
			return backend_error_message()

		payload = {
			"ward_code": ward_code,
			"crop": crop_code,
			"crop_label": crop_label,
			"acreage": str(acreage),
			"message": result.get("message", "Premium quote pending agent review."),
		}
		return screens.registration_complete(payload)
