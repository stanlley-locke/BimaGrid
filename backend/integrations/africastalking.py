"""Africa's Talking SMS integration."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AfricasTalkingClient:
	def __init__(self) -> None:
		self.username = settings.AFRICASTALKING_USERNAME
		self.api_key = settings.AFRICASTALKING_API_KEY
		self.sender_id = settings.AFRICASTALKING_SENDER_ID
		self.use_mock = settings.AFRICASTALKING_USE_MOCK
		self.base_url = "https://api.africastalking.com/version1"

	def send_sms(self, to: str | list[str], message: str) -> dict[str, Any]:
		recipients = to if isinstance(to, list) else [to]
		if self.use_mock:
			logger.info("Mock SMS to %s: %s", recipients, message[:80])
			return {
				"SMSMessageData": {
					"Message": f"Mock sent to {len(recipients)} recipient(s)",
					"Recipients": [
						{
							"statusCode": "101",
							"number": phone,
							"status": "Success",
							"messageId": f"MOCK-{phone[-4:]}",
						}
						for phone in recipients
					],
				}
			}

		response = requests.post(
			f"{self.base_url}/messaging",
			headers={"apiKey": self.api_key, "Accept": "application/json"},
			data={
				"username": self.username,
				"to": ",".join(recipients),
				"message": message,
				"from": self.sender_id,
			},
			timeout=30,
		)
		response.raise_for_status()
		return response.json()
