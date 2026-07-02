"""USSD gateway request parsing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.utils.parsing import parse_ussd_text
from src.utils.phone import normalize_phone


@dataclass(frozen=True)
class UssdRequest:
	session_id: str
	phone_number: str
	text: str
	service_code: str
	network_code: str

	@property
	def steps(self) -> list[str]:
		return parse_ussd_text(self.text)

	@property
	def normalized_phone(self) -> str:
		return normalize_phone(self.phone_number)


def parse_ussd_request(data: dict[str, Any]) -> UssdRequest:
	"""Parse Africa's Talking USSD webhook payload."""
	return UssdRequest(
		session_id=str(data.get("sessionId", "")).strip(),
		phone_number=str(data.get("phoneNumber", "")).strip(),
		text=str(data.get("text", "")).strip(),
		service_code=str(data.get("serviceCode", "")).strip(),
		network_code=str(data.get("networkCode", "")).strip(),
	)


def validate_ussd_request(request: UssdRequest) -> tuple[bool, str]:
	if not request.session_id:
		return False, "sessionId is required"
	if not request.phone_number:
		return False, "phoneNumber is required"
	return True, ""
