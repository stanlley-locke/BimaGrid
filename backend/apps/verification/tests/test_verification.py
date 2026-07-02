from unittest.mock import patch
import pytest

from apps.onboarding.constants import OnboardingStatus
from apps.verification.models import VerificationRecord
from apps.verification.services import create_verification_record, mark_verification_reviewed
from apps.verification.satellite import verify_irrigation
from apps.verification.image_analysis import analyze_farm_image
from tests.factories import FarmerOnboardingFactory, UserFactory


@pytest.mark.django_db
class TestVerificationServices:
    def test_create_and_review_verification_record(self):
        onboarding = FarmerOnboardingFactory()
        user = UserFactory()
        
        record = create_verification_record(
            onboarding,
            {"verification_type": "mitigation"}
        )
        assert record.id is not None
        assert record.status == VerificationRecord.Status.PENDING
        
        mark_verification_reviewed(
            record,
            reviewer=user,
            status=VerificationRecord.Status.APPROVED,
            findings="Drip irrigation lines verified via satellite."
        )
        assert record.status == VerificationRecord.Status.APPROVED
        assert record.reviewed_by == user
        assert record.reviewed_at is not None
        assert record.findings == "Drip irrigation lines verified via satellite."

    @patch("apps.verification.satellite.get_openeo_client")
    def test_verify_irrigation(self, mock_get_client):
        mock_client = mock_get_client.return_value
        mock_client.compute_ndwi.return_value = {
            "mean": 0.40,
            "source": "sentinel-2"
        }
        
        result = verify_irrigation("8928308280fffff")
        assert result["verified"] is True
        assert result["mean_ndwi"] == 0.40
        assert result["mitigation"] == "drip_irrigation"

    def test_analyze_farm_image(self):
        dummy_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        result = analyze_farm_image(dummy_image)
        
        assert "scores" in result
        assert "checksum" in result
        assert len(result["detected_features"]) >= 1
