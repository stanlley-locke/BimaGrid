"""Payments Celery tasks."""

from __future__ import annotations

from decimal import Decimal

from celery import shared_task

from apps.notifications.tasks import send_payout_sms
from apps.policies.models import Policy

from .services import execute_payout, queue_payout


@shared_task
def process_payout_trigger(policy_id: str, amount_kes: float, tx_hash: str, event: str) -> dict:
	policy = Policy.objects.select_related("onboarding").get(policy_number=policy_id)
	phone = policy.onboarding.mpesa_number
	payout = queue_payout(policy, Decimal(str(amount_kes)), phone)
	execute_payout(payout)
	send_payout_sms.delay(phone, float(amount_kes), policy.policy_number, tx_hash)
	return {"payout_id": str(payout.id), "event": event, "policy_id": policy_id}


@shared_task
def dispatch_queued_payout(payout_id: str) -> str:
	from .models import Payout

	payout = Payout.objects.select_related("policy").get(id=payout_id)
	execute_payout(payout)
	return str(payout.id)
