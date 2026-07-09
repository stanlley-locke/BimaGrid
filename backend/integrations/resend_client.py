"""Resend Email integration."""

from __future__ import annotations

import logging
from typing import Any

import resend
from django.conf import settings

logger = logging.getLogger(__name__)

class ResendClient:
    def __init__(self) -> None:
        self.api_key = getattr(settings, "RESEND_API_KEY", "re_mock_key")
        self.sender_email = getattr(settings, "RESEND_SENDER_EMAIL", "onboarding@bimagrid.com")
        resend.api_key = self.api_key
        self.use_mock = getattr(settings, "RESEND_USE_MOCK", False)

    def send_email(self, to: str | list[str], subject: str, html_body: str) -> dict[str, Any]:
        recipients = to if isinstance(to, list) else [to]
        if self.use_mock or self.api_key == "re_mock_key":
            logger.info("Mock Email to %s: %s", recipients, subject)
            return {"id": "mock_email_id_123"}
            
        try:
            params = {
                "from": self.sender_email,
                "to": recipients,
                "subject": subject,
                "html": html_body,
            }
            response = resend.Emails.send(params)
            return response
        except Exception as exc:
            logger.error("Resend API failed: %s", exc)
            raise
