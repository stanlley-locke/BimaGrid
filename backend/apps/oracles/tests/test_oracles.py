import pytest
from decimal import Decimal

from apps.core.exceptions import OracleSignatureError
from apps.oracles.models import OracleSubmission, OracleConsensus
from apps.oracles.aggregators import (
    build_submission_hash,
    verify_oracle_signature,
    median_of_submissions,
    blend_rainfall_sources,
    evaluate_drought_trigger,
    consensus_ready,
    aggregate_submissions
)


class TestOracleAggregators:
    def test_build_submission_hash(self):
        payload = {"h3": "8928308280fffff", "rainfall": 15.2}
        h1 = build_submission_hash(payload)
        # Order of keys should not affect hash
        payload_alt = {"rainfall": 15.2, "h3": "8928308280fffff"}
        h2 = build_submission_hash(payload_alt)
        assert h1 == h2

    def test_verify_oracle_signature_mock(self, settings):
        settings.ORACLE_SIGNATURE_VERIFY = True
        settings.DEBUG = True
        payload = {"h3": "8928308280fffff"}
        assert verify_oracle_signature(payload, "mock:test-signature") is True

    def test_verify_oracle_signature_authorized(self, settings):
        settings.ORACLE_SIGNATURE_VERIFY = True
        settings.ORACLE_AUTHORIZED_KEYS = ["key123"]
        payload = {"h3": "8928308280fffff"}
        h = build_submission_hash(payload)
        
        import hashlib
        expected_sig = hashlib.sha256(f"{h}:key123".encode()).hexdigest()
        
        assert verify_oracle_signature(payload, expected_sig) is True

        with pytest.raises(OracleSignatureError):
            verify_oracle_signature(payload, "invalid-sig")

    def test_median_of_submissions(self):
        # We need to construct mock submissions (doesn't need to be in DB)
        s1 = OracleSubmission(metric_value=Decimal("10.00"))
        s2 = OracleSubmission(metric_value=Decimal("15.00"))
        s3 = OracleSubmission(metric_value=Decimal("20.00"))
        
        assert median_of_submissions([s1, s2, s3]) == Decimal("15.0000")

    def test_blend_rainfall_sources(self):
        sources = {"chirps": 12.0, "open-meteo": 10.0}
        # weights: chirps=0.5, open-meteo=0.2
        # weighted_sum = 12 * 0.5 + 10 * 0.2 = 6.0 + 2.0 = 8.0
        # total_weight = 0.5 + 0.2 = 0.7
        # result = 8.0 / 0.7 = 11.42857
        assert pytest.approx(blend_rainfall_sources(sources)) == 11.42857

    def test_evaluate_drought_trigger(self):
        assert evaluate_drought_trigger(15.0, 20.0) is True
        assert evaluate_drought_trigger(25.0, 20.0) is False


@pytest.mark.django_db
class TestOracleConsensusDB:
    def test_consensus_ready_and_aggregate(self):
        h3_index = "8928308280fffff"
        metric = "rainfall"
        
        # Initially not ready
        assert not consensus_ready(h3_index, metric)

        s1 = OracleSubmission.objects.create(
            oracle_name="Oracle A",
            h3_index=h3_index,
            metric_name=metric,
            metric_value=Decimal("15.50"),
            data_hash="hash1"
        )
        s2 = OracleSubmission.objects.create(
            oracle_name="Oracle B",
            h3_index=h3_index,
            metric_name=metric,
            metric_value=Decimal("17.00"),
            data_hash="hash2"
        )
        s3 = OracleSubmission.objects.create(
            oracle_name="Oracle C",
            h3_index=h3_index,
            metric_name=metric,
            metric_value=Decimal("16.00"),
            data_hash="hash3"
        )

        assert consensus_ready(h3_index, metric)

        agg = aggregate_submissions([s1, s2, s3])
        assert agg["oracle_count"] == 3
        assert agg["metrics"][metric]["median"] == "16.0000"
