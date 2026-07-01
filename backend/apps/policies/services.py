"""Policy services."""

from __future__ import annotations

from django.db import transaction

from apps.core.utils import build_reference_code

from .models import Policy, PolicyEvent


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
