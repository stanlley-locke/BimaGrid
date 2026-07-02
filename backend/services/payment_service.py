"""Payment orchestration service."""

from __future__ import annotations

from apps.payments.services import bypass_payment_for_policy, execute_payout, initiate_stk_payment, queue_payout
from apps.policies.models import Policy


def collect_premium(policy: Policy, phone_number: str):
	return initiate_stk_payment(policy, phone_number)


def process_payout_for_policy(policy: Policy, amount, phone_number: str):
	payout = queue_payout(policy, amount, phone_number)
	return execute_payout(payout)


def admin_bypass_payment(policy: Policy):
	return bypass_payment_for_policy(policy)
