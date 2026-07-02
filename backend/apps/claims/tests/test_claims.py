import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.claims.models import Claim
from apps.claims.services import open_claim, evaluate_parametric_claim
from tests.factories import PolicyFactory, ProfileFactory, UserFactory


@pytest.mark.django_db
class TestClaimsService:
    def test_open_claim_success(self):
        policy = PolicyFactory()
        claim_data = {
            "loss_type": "Drought",
            "description": "Severe lack of rain in Resolution 9 cell",
            "claimed_amount": Decimal("1000.00"),
            "threshold_value": Decimal("20.00"),
        }
        claim = open_claim(policy, claim_data)
        assert claim.id is not None
        assert claim.claim_number.startswith("CLM")
        assert claim.loss_type == "Drought"
        assert claim.status == Claim.Status.DRAFT
        assert claim.reviews.count() == 1
        assert claim.reviews.first().decision == "draft"

    def test_evaluate_parametric_claim_trigger_met(self):
        policy = PolicyFactory()
        claim = Claim.objects.create(
            policy=policy,
            claim_number="CLM-TEST-001",
            loss_type="Drought",
            claimed_amount=Decimal("1000.00"),
            threshold_value=Decimal("20.00")
        )
        evaluate_parametric_claim(claim, 15.00)
        assert claim.status == Claim.Status.APPROVED
        assert claim.trigger_value == Decimal("15.00")
        assert claim.reviews.count() == 1
        assert claim.reviews.first().decision == "approved"

    def test_evaluate_parametric_claim_trigger_not_met(self):
        policy = PolicyFactory()
        claim = Claim.objects.create(
            policy=policy,
            claim_number="CLM-TEST-002",
            loss_type="Drought",
            claimed_amount=Decimal("1000.00"),
            threshold_value=Decimal("20.00")
        )
        evaluate_parametric_claim(claim, 25.00)
        assert claim.status == Claim.Status.REJECTED
        assert claim.trigger_value == Decimal("25.00")
        assert claim.reviews.count() == 1
        assert claim.reviews.first().decision == "rejected"


@pytest.mark.django_db
class TestClaimsApi:
    @pytest.fixture(autouse=True)
    def setup_api(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.profile = ProfileFactory(user=self.user, role=Profile.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.policy = PolicyFactory()

    def test_list_claims(self):
        Claim.objects.create(
            policy=self.policy,
            claim_number="CLM-001",
            loss_type="Drought",
            claimed_amount=Decimal("500.00")
        )
        response = self.client.get("/api/claims/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["claim_number"] == "CLM-001"

    def test_create_claim(self):
        payload = {
            "policy": str(self.policy.id),
            "loss_type": "Drought",
            "description": "Famine",
            "claimed_amount": "5000.00",
            "threshold_value": "20.00"
        }
        response = self.client.post("/api/claims/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["claim_number"].startswith("CLM")
        assert Claim.objects.filter(claim_number=data["claim_number"]).exists()
