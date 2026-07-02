"""Notification orchestration service."""

from __future__ import annotations

from apps.notifications.services import dispatch_notification
from apps.notifications.tasks import send_payout_sms


def notify_payout(phone: str, amount: float, policy_id: str, tx_hash: str) -> dict:
	return send_payout_sms(phone, amount, policy_id, tx_hash)


def notify_user(user, subject: str, body: str, channel: str = "sms", metadata: dict | None = None):
	return dispatch_notification(user, subject, body, channel=channel, metadata=metadata)
