"""Africa's Talking SMS integration."""

from __future__ import annotations

from integrations.africastalking import AfricasTalkingClient


def send_sms(to: str | list[str], message: str) -> dict:
	return AfricasTalkingClient().send_sms(to, message)
