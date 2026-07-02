"""M-Pesa webhook handlers."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.policies.services import activate_policy, mark_policy_paid_out

from .models import PaymentTransaction, Payout
from .services import complete_payout, process_stk_callback

logger = logging.getLogger(__name__)


def handle_stk_callback(payload: dict[str, Any]) -> PaymentTransaction | None:
	body = payload.get("Body", {}).get("stkCallback", {})
	checkout_id = body.get("CheckoutRequestID")
	result_code = body.get("ResultCode")
	if checkout_id is None:
		logger.warning("STK callback missing CheckoutRequestID")
		return None
	return process_stk_callback(checkout_id, result_code, body)


def handle_b2c_result(payload: dict[str, Any]) -> Payout | None:
	result = payload.get("Result", {})
	originator_id = result.get("OriginatorConversationID")
	result_code = result.get("ResultCode")
	payout = Payout.objects.filter(reference=originator_id).first()
	if not payout:
		params = {
			item.get("Key"): item.get("Value")
			for item in result.get("ResultParameters", {}).get("ResultParameter", [])
		}
		receipt = params.get("TransactionReceipt")
		if receipt:
			payout = Payout.objects.filter(tx_hash=receipt).first()
	if not payout:
		logger.warning("B2C result for unknown payout: %s", originator_id)
		return None
	if result_code == 0:
		complete_payout(payout, tx_hash=result.get("TransactionID", ""))
	else:
		payout.status = "failed"
		payout.save(update_fields=["status", "updated_at"])
	return payout


def handle_b2c_timeout(payload: dict[str, Any]) -> None:
	result = payload.get("Result", {})
	logger.warning("B2C timeout for %s", result.get("OriginatorConversationID"))


def handle_payout_trigger(payload: dict[str, Any]) -> dict[str, Any]:
	from .tasks import process_payout_trigger

	policy_id = payload.get("policy_id")
	amount = payload.get("amount_kes")
	tx_hash = payload.get("tx_hash", "")
	event = payload.get("event", "PayoutAuthorized")
	result = process_payout_trigger.delay(policy_id, amount, tx_hash, event)
	if hasattr(result, "id"):
		return {"task_id": result.id, "status": "queued"}
	return result
