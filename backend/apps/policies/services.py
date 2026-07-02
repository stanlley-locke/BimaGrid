"""Policy services."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.core.utils import build_reference_code

from .constants import POLICY_TRANSITIONS
from .models import Policy, PolicyEvent


class InvalidPolicyTransition(Exception):
	pass


def can_transition(current_status: str, new_status: str) -> bool:
	return new_status in POLICY_TRANSITIONS.get(current_status, set())


@transaction.atomic
def transition_policy(policy: Policy, new_status: str, event_type: str, details: dict | None = None) -> Policy:
	if not can_transition(policy.status, new_status):
		raise InvalidPolicyTransition(f"Cannot transition from {policy.status} to {new_status}")
	policy.status = new_status
	policy.save(update_fields=["status", "updated_at"])
	PolicyEvent.objects.create(policy=policy, event_type=event_type, details=details or {"status": new_status})
	return policy


@transaction.atomic
def issue_policy(onboarding, policy_data: dict) -> Policy:
	policy_number = policy_data.pop("policy_number", None) or build_reference_code("POL")
	policy = Policy.objects.create(
		onboarding=onboarding,
		policy_number=policy_number,
		**policy_data,
	)
	PolicyEvent.objects.create(policy=policy, event_type="issued", details={"status": policy.status})
	return policy


def activate_policy(policy: Policy) -> Policy:
	return transition_policy(policy, Policy.Status.ACTIVE, "activated", {"activated_at": timezone.now().isoformat()})


def mark_policy_paid_out(policy: Policy) -> Policy:
	return transition_policy(
		policy,
		Policy.Status.PAID_OUT,
		"payout_completed",
		{"paid_out_at": timezone.now().isoformat()},
	)


def lapse_policy(policy: Policy) -> Policy:
	return transition_policy(policy, Policy.Status.LAPSED, "lapsed")
