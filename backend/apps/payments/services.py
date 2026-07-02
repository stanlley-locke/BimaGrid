"""Payments services."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.core.utils import build_reference_code
from apps.policies.models import Policy
from apps.policies.services import activate_policy, mark_policy_paid_out
from integrations.mpesa import MpesaClient

from .models import PaymentTransaction, Payout


def initiate_stk_payment(policy: Policy, phone_number: str) -> PaymentTransaction:
	client = MpesaClient()
	response = client.stk_push(
		phone_number=phone_number,
		amount=float(policy.premium_amount),
		account_reference=policy.policy_number,
	)
	payment = PaymentTransaction.objects.create(
		policy=policy,
		provider="mpesa",
		reference=build_reference_code("PAY"),
		amount=policy.premium_amount,
		status=PaymentTransaction.Status.PROCESSING,
		provider_payload=response,
	)
	return payment


def record_payment(policy=None, claim=None, amount=0, provider="mpesa", payload=None) -> PaymentTransaction:
	return PaymentTransaction.objects.create(
		policy=policy,
		claim=claim,
		provider=provider,
		reference=build_reference_code("PAY"),
		amount=amount,
		status=PaymentTransaction.Status.SUCCESS,
		provider_payload=payload or {},
		processed_at=timezone.now(),
	)


@transaction.atomic
def process_stk_callback(checkout_id: str, result_code: int, body: dict) -> PaymentTransaction | None:
	payment = PaymentTransaction.objects.filter(provider_payload__CheckoutRequestID=checkout_id).first()
	if not payment:
		payment = PaymentTransaction.objects.filter(provider_payload__checkout_request_id=checkout_id).first()
	if not payment:
		return None
	if result_code == 0:
		payment.status = PaymentTransaction.Status.SUCCESS
		payment.processed_at = timezone.now()
		if payment.policy:
			activate_policy(payment.policy)
	else:
		payment.status = PaymentTransaction.Status.FAILED
	payment.provider_payload = {**payment.provider_payload, "callback": body}
	payment.save()
	return payment


def queue_payout(policy, amount, phone_number) -> Payout:
	payout = Payout.objects.create(
		policy=policy,
		amount=amount,
		phone_number=phone_number,
		reference=build_reference_code("PYO"),
		status="queued",
	)
	return payout


@transaction.atomic
def execute_payout(payout: Payout) -> Payout:
	client = MpesaClient()
	response = client.b2c_payout(
		phone_number=payout.phone_number,
		amount=float(payout.amount),
		occasion=payout.policy.policy_number,
	)
	payout.status = "processing"
	payout.tx_hash = response.get("ConversationID", "")
	payout.save(update_fields=["status", "tx_hash", "updated_at"])
	return payout


def complete_payout(payout: Payout, tx_hash: str = "") -> Payout:
	payout.status = "completed"
	if tx_hash:
		payout.tx_hash = tx_hash
	payout.save(update_fields=["status", "tx_hash", "updated_at"])
	mark_policy_paid_out(payout.policy)
	return payout


def bypass_payment_for_policy(policy: Policy) -> PaymentTransaction:
	payment = record_payment(
		policy=policy,
		amount=policy.premium_amount,
		payload={"bypass": True, "source": "admin"},
	)
	activate_policy(policy)
	return payment
