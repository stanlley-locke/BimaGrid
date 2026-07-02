"""Policy Django signals."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Policy


@receiver(post_save, sender=Policy)
def notify_policy_change(sender, instance: Policy, created: bool, **kwargs) -> None:
	if created or instance.status != Policy.Status.PAID_OUT:
		return
	from apps.notifications.tasks import send_notification_async

	onboarding = instance.onboarding
	user = onboarding.profile.user
	send_notification_async.delay(
		user.id,
		"Policy payout completed",
		f"Policy {instance.policy_number} has been paid out.",
		channel="sms",
		metadata={"phone": onboarding.mpesa_number},
	)
