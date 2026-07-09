"""Email notification delivery."""

from __future__ import annotations

import logging
import os

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(to: str | list[str], subject: str, body: str) -> bool:
	recipients = to if isinstance(to, list) else [to]
	
	# Try Resend API first if configured
	resend_api_key = getattr(settings, "RESEND_API_KEY", None) or os.environ.get("RESEND_API_KEY")
	if resend_api_key:
		try:
			import requests
			response = requests.post(
				"https://api.resend.com/emails",
				headers={
					"Authorization": f"Bearer {resend_api_key}",
					"Content-Type": "application/json",
				},
				json={
					"from": getattr(settings, "DEFAULT_FROM_EMAIL", "onboarding@resend.dev"),
					"to": recipients,
					"subject": subject,
					"text": body,
				},
				timeout=15,
			)
			if response.status_code in (200, 201, 202):
				return True
			logger.warning("Resend API returned status %s: %s. Falling back to send_mail.", response.status_code, response.text)
		except Exception as exc:
			logger.warning("Resend delivery failed: %s. Falling back to send_mail.", exc)

	# Fallback to standard Django send_mail
	try:
		send_mail(
			subject=subject,
			message=body,
			from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@bimagrid.io"),
			recipient_list=recipients,
			fail_silently=False,
		)
		return True
	except Exception as exc:
		logger.warning("Email delivery failed: %s", exc)
		return False
