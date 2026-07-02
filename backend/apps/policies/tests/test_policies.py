import pytest
from datetime import date
from decimal import Decimal

from apps.policies.models import Policy, PolicyEvent
from apps.policies.services import (
    can_transition,
    transition_policy,
    issue_policy,
    activate_policy,
    mark_policy_paid_out,
    lapse_policy,
    InvalidPolicyTransition
)
from tests.factories import FarmerOnboardingFactory, PolicyFactory


@pytest.mark.django_db
class TestPolicyServices:
    def test_can_transition_validation(self):
        assert can_transition(Policy.Status.DRAFT, Policy.Status.ACTIVE) is True
        assert can_transition(Policy.Status.ACTIVE, Policy.Status.PAID_OUT) is True
        # Cannot go from ACTIVE back to DRAFT
        assert can_transition(Policy.Status.ACTIVE, Policy.Status.DRAFT) is False

    def test_transition_policy_success(self):
        policy = PolicyFactory(status=Policy.Status.DRAFT)
        transition_policy(policy, Policy.Status.ACTIVE, "activated")
        assert policy.status == Policy.Status.ACTIVE
        assert policy.events.count() == 1
        assert policy.events.first().event_type == "activated"

    def test_transition_policy_invalid_raises_error(self):
        policy = PolicyFactory(status=Policy.Status.ACTIVE)
        with pytest.raises(InvalidPolicyTransition):
            transition_policy(policy, Policy.Status.DRAFT, "reset")

    def test_issue_policy(self):
        onboarding = FarmerOnboardingFactory()
        policy_data = {
            "crop": "MAIZE",
            "insured_acreage": Decimal("3.00"),
            "coverage_h3": "8928308280fffff",
            "premium_amount": Decimal("300.00"),
            "coverage_start": date.today(),
            "coverage_end": date.today(),
            "status": Policy.Status.DRAFT
        }
        policy = issue_policy(onboarding, policy_data)
        assert policy.id is not None
        assert policy.policy_number.startswith("POL")
        assert policy.status == Policy.Status.DRAFT
        assert policy.events.count() == 1

    def test_specific_transitions(self):
        policy = PolicyFactory(status=Policy.Status.DRAFT)
        
        # Activate
        activate_policy(policy)
        assert policy.status == Policy.Status.ACTIVE
        
        # Payout
        mark_policy_paid_out(policy)
        assert policy.status == Policy.Status.PAID_OUT

        # Lapse (reset status to test lapse)
        policy.status = Policy.Status.ACTIVE
        policy.save()
        lapse_policy(policy)
        assert policy.status == Policy.Status.LAPSED
