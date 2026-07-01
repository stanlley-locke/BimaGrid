"""Notification services."""

from __future__ import annotations

from django.utils import timezone

from .models import Notification


def dispatch_notification(user, subject: str, body: str, channel: str = "email", template=None, metadata: dict | None = None) -> Notification:
	notification = Notification.objects.create(
		user=user,
		template=template,
		channel=channel,
		subject=subject,
		body=body,
		status=Notification.Status.SENT,
		delivered_at=timezone.now(),
		metadata=metadata or {},
	)
	return notification
