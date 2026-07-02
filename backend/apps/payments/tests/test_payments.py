from unittest.mock import patch
import pytest
from decimal import Decimal

from apps.payments.models import PaymentTransaction, Payout
from apps.payments.services import (
    initiate_stk_payment,
    record_payment,
    process_stk_callback,
    queue_payout,
    execute_payout,
    complete_payout,
    bypass_payment_for_policy
)
from apps.policies.models import Policy
from tests.factories import PolicyFactory


@pytest.mark.django_db
class TestPaymentsService:
    @patch("apps.payments.services.MpesaClient")
    def test_initiate_stk_payment(self, mock_mpesa_class):
        mock_client = mock_mpesa_class.return_value
        mock_client.stk_push.return_value = {"CheckoutRequestID": "ws_CO_00000"}
        
        policy = PolicyFactory(premium_amount=Decimal("150.00"))
        payment = initiate_stk_payment(policy, "+254712345678")
        
        assert payment.id is not None
        assert payment.amount == Decimal("150.00")
        assert payment.status == PaymentTransaction.Status.PROCESSING
        assert payment.provider_payload["CheckoutRequestID"] == "ws_CO_00000"
        mock_client.stk_push.assert_called_once_with(
            phone_number="+254712345678",
            amount=150.0,
            account_reference=policy.policy_number
        )

    def test_record_payment(self):
        policy = PolicyFactory()
        payment = record_payment(
            policy=policy,
            amount=Decimal("200.00"),
            payload={"source": "cash"}
        )
        assert payment.id is not None
        assert payment.amount == Decimal("200.00")
        assert payment.status == PaymentTransaction.Status.SUCCESS
        assert payment.processed_at is not None

    def test_process_stk_callback_success(self):
        policy = PolicyFactory(status=Policy.Status.DRAFT)
        payment = PaymentTransaction.objects.create(
            policy=policy,
            amount=policy.premium_amount,
            reference="PAY-REF-001",
            status=PaymentTransaction.Status.PROCESSING,
            provider_payload={"CheckoutRequestID": "ws_CO_123"}
        )
        
        process_stk_callback("ws_CO_123", 0, {"ResultDesc": "Success"})
        payment.refresh_from_db()
        policy.refresh_from_db()
        
        assert payment.status == PaymentTransaction.Status.SUCCESS
        assert policy.status == Policy.Status.ACTIVE

    def test_process_stk_callback_failed(self):
        policy = PolicyFactory(status=Policy.Status.DRAFT)
        payment = PaymentTransaction.objects.create(
            policy=policy,
            amount=policy.premium_amount,
            reference="PAY-REF-002",
            status=PaymentTransaction.Status.PROCESSING,
            provider_payload={"CheckoutRequestID": "ws_CO_456"}
        )
        
        process_stk_callback("ws_CO_456", 1032, {"ResultDesc": "Cancelled"})
        payment.refresh_from_db()
        policy.refresh_from_db()
        
        assert payment.status == PaymentTransaction.Status.FAILED
        assert policy.status == Policy.Status.DRAFT

    def test_queue_payout(self):
        policy = PolicyFactory()
        payout = queue_payout(policy, Decimal("5000.00"), "+254712345678")
        assert payout.id is not None
        assert payout.status == "queued"
        assert payout.amount == Decimal("5000.00")

    @patch("apps.payments.services.MpesaClient")
    def test_execute_payout(self, mock_mpesa_class):
        mock_client = mock_mpesa_class.return_value
        mock_client.b2c_payout.return_value = {"ConversationID": "AG_2026_01"}
        
        policy = PolicyFactory()
        payout = Payout.objects.create(
            policy=policy,
            amount=Decimal("500.00"),
            phone_number="+254712345678",
            reference="PYO-REF-001",
            status="queued"
        )
        
        execute_payout(payout)
        payout.refresh_from_db()
        
        assert payout.status == "processing"
        assert payout.tx_hash == "AG_2026_01"
        mock_client.b2c_payout.assert_called_once_with(
            phone_number="+254712345678",
            amount=500.0,
            occasion=policy.policy_number
        )

    def test_complete_payout(self):
        policy = PolicyFactory(status=Policy.Status.ACTIVE)
        payout = Payout.objects.create(
            policy=policy,
            amount=Decimal("500.00"),
            phone_number="+254712345678",
            reference="PYO-REF-002",
            status="processing",
            tx_hash="AG_002"
        )
        
        complete_payout(payout, "NEW_TX_HASH")
        payout.refresh_from_db()
        policy.refresh_from_db()
        
        assert payout.status == "completed"
        assert payout.tx_hash == "NEW_TX_HASH"
        assert policy.status == Policy.Status.PAID_OUT

    def test_bypass_payment(self):
        policy = PolicyFactory(status=Policy.Status.DRAFT)
        payment = bypass_payment_for_policy(policy)
        policy.refresh_from_db()
        
        assert payment.status == PaymentTransaction.Status.SUCCESS
        assert policy.status == Policy.Status.ACTIVE
