"""Notifications Celery tasks."""

from __future__ import annotations

from celery import shared_task

from django.contrib.auth import get_user_model

from .services import dispatch_notification
from .sms import send_sms

User = get_user_model()


@shared_task
def send_payout_sms(phone: str, amount: float, policy_id: str, tx_hash: str) -> dict:
	message = (
		f"BimaGrid Alert: Drought detected in your area. KES {amount:,.0f} sent to your M-Pesa account. "
		f"Policy: {policy_id}. Tx: {tx_hash}"
	)
	return send_sms(phone, message)


@shared_task
def send_notification_async(user_id: int, subject: str, body: str, channel: str = "sms", metadata: dict | None = None) -> str:
	user = User.objects.get(id=user_id)
	notification = dispatch_notification(user, subject, body, channel=channel, metadata=metadata)
	return str(notification.id)


@shared_task
def send_farmer_welcome_notifications(user_id: int, password: str) -> None:
	user = User.objects.get(id=user_id)
	profile = getattr(user, "profile", None)
	
	subject = "Welcome to BimaGrid Protection Plan"
	body = (
		f"Dear {profile.full_name if profile else user.username},\n\n"
		f"Welcome to BimaGrid! Your farmer account has been created successfully.\n"
		f"Your Username: {user.username}\n"
		f"Your Password: {password}\n"
		f"Your Phone Number: {profile.phone_number if profile else '—'}\n\n"
		f"You can view your active policies and file claims via USSD using your phone.\n\n"
		f"Best regards,\nBimaGrid Team"
	)
	
	# Send SMS via Africa's Talking
	phone = profile.phone_number if profile else None
	if phone:
		dispatch_notification(user, subject, body, channel="sms", metadata={"phone": phone})
		
	# Send Email (if set) via Resend
	if user.email:
		dispatch_notification(user, subject, body, channel="email")
