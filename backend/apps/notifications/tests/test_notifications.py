from unittest.mock import patch
import pytest

from apps.notifications.models import Notification
from apps.notifications.services import dispatch_notification
from tests.factories import UserFactory


@pytest.mark.django_db
class TestNotificationsService:
    @patch("apps.notifications.services.send_email")
    def test_dispatch_notification_email_success(self, mock_send_email):
        mock_send_email.return_value = True
        user = UserFactory()
        
        notification = dispatch_notification(
            user=user,
            subject="Test Subject",
            body="Test Email Body",
            channel="email"
        )
        
        assert notification.id is not None
        assert notification.status == Notification.Status.SENT
        assert notification.channel == "email"
        assert notification.delivered_at is not None
        mock_send_email.assert_called_once_with(user.email, "Test Subject", "Test Email Body")

    @patch("apps.notifications.services.send_email")
    def test_dispatch_notification_email_failed(self, mock_send_email):
        mock_send_email.return_value = False
        user = UserFactory()
        
        notification = dispatch_notification(
            user=user,
            subject="Test Subject",
            body="Test Email Body",
            channel="email"
        )
        
        assert notification.status == Notification.Status.FAILED
        assert notification.delivered_at is None

    @patch("apps.notifications.services.send_sms")
    def test_dispatch_notification_sms_success(self, mock_send_sms):
        # send_sms response format checks SMSMessageData -> Recipients
        mock_send_sms.return_value = {
            "SMSMessageData": {
                "Recipients": [{"status": "Success", "number": "+254712345678"}]
            }
        }
        user = UserFactory()
        
        notification = dispatch_notification(
            user=user,
            subject="SMS Alert",
            body="Test SMS Body",
            channel="sms",
            metadata={"phone": "+254712345678"}
        )
        
        assert notification.status == Notification.Status.SENT
        assert notification.delivered_at is not None
        mock_send_sms.assert_called_once_with("+254712345678", "Test SMS Body")
