"""Email notification delivery."""

from __future__ import annotations

import logging

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(to: str | list[str], subject: str, body: str) -> bool:
	recipients = to if isinstance(to, list) else [to]
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
