"""Notification services."""

from __future__ import annotations

from django.utils import timezone

from .email import send_email
from .models import Notification
from .sms import send_sms


def dispatch_notification(user, subject: str, body: str, channel: str = "email", template=None, metadata: dict | None = None) -> Notification:
	notification = Notification.objects.create(
		user=user,
		template=template,
		channel=channel,
		subject=subject,
		body=body,
		status=Notification.Status.PENDING,
		metadata=metadata or {},
	)
	delivered = False
	if channel == "sms":
		phone = metadata.get("phone") if metadata else None
		if phone:
			response = send_sms(phone, body)
			delivered = bool(response.get("SMSMessageData", {}).get("Recipients"))
	elif channel == "email":
		email = user.email if user else metadata.get("email") if metadata else None
		if email:
			delivered = send_email(email, subject, body)
	else:
		delivered = True

	if delivered:
		notification.status = Notification.Status.SENT
		notification.delivered_at = timezone.now()
	else:
		notification.status = Notification.Status.FAILED
	notification.save(update_fields=["status", "delivered_at", "updated_at"])
	return notification
