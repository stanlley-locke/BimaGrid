from unittest.mock import patch
import pytest

from apps.satellite.openeo_client import get_openeo_client
from integrations.openeo import OpenEOClient


class TestSatelliteClient:
    def test_mock_openeo_ndvi(self, settings):
        settings.OPENEO_USE_MOCK = True
        client = get_openeo_client()
        assert isinstance(client, OpenEOClient)
        
        result = client.compute_ndvi(
            h3_index="8928308280fffff",
            spatial_extent={"east": 36.8, "west": 36.7, "north": -1.2, "south": -1.3}
        )
        
        assert result["h3_index"] == "8928308280fffff"
        assert result["index"] == "ndvi"
        assert result["source"] == "mock-openeo"
        assert 0.2 <= result["mean"] <= 0.8

    def test_mock_openeo_ndwi(self, settings):
        settings.OPENEO_USE_MOCK = True
        client = get_openeo_client()
        
        result = client.compute_ndwi(
            h3_index="8928308280fffff",
            spatial_extent={"east": 36.8, "west": 36.7, "north": -1.2, "south": -1.3}
        )
        
        assert result["h3_index"] == "8928308280fffff"
        assert result["index"] == "ndwi"
        assert -0.1 <= result["mean"] <= 0.4

    def test_mock_openeo_evi(self, settings):
        settings.OPENEO_USE_MOCK = True
        client = get_openeo_client()
        
        result = client.compute_evi(
            h3_index="8928308280fffff",
            spatial_extent={"east": 36.8, "west": 36.7, "north": -1.2, "south": -1.3}
        )
        
        assert result["h3_index"] == "8928308280fffff"
        assert result["index"] == "evi"
        assert 0.15 <= result["mean"] <= 0.70

    @patch("integrations.openeo.requests.post")
    def test_live_openeo_ndvi(self, mock_post, settings):
        settings.OPENEO_USE_MOCK = False
        settings.OPENEO_BACKEND_URL = "http://openeo.test"
        
        mock_response = mock_post.return_value
        mock_response.json.return_value = {
            "mean": 0.5432,
            "source": "live-sentinel"
        }
        
        client = get_openeo_client()
        result = client.compute_ndvi(
            h3_index="8928308280fffff",
            spatial_extent={"east": 36.8, "west": 36.7, "north": -1.2, "south": -1.3}
        )
        
        assert result["mean"] == 0.5432
        assert result["h3_index"] == "8928308280fffff"
        mock_post.assert_called_once()
