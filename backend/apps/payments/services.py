"""Payments services."""

from __future__ import annotations

from django.utils import timezone

from apps.core.utils import build_reference_code

from .models import PaymentTransaction, Payout


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


def queue_payout(policy, amount, phone_number) -> Payout:
	return Payout.objects.create(
		policy=policy,
		amount=amount,
		phone_number=phone_number,
		reference=build_reference_code("PYO"),
	)
