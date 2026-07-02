import pytest
from decimal import Decimal

from apps.geospatial.models import H3Grid, GridRisk
from apps.geospatial.h3_utils import (
    lat_lng_to_h3,
    h3_to_lat_lng,
    h3_to_boundary_geojson,
    geojson_centroid,
    h3_index_from_geojson,
    polyfill_geojson
)


class TestH3Utils:
    def test_lat_lng_to_h3_and_back(self):
        lat, lng = -1.2921, 36.8219  # Nairobi
        h3_idx = lat_lng_to_h3(lat, lng, resolution=9)
        assert h3_idx is not None
        assert len(h3_idx) == 15
        
        lat_back, lng_back = h3_to_lat_lng(h3_idx)
        assert abs(lat_back - lat) < 0.1
        assert abs(lng_back - lng) < 0.1

    def test_h3_to_boundary_geojson(self):
        h3_idx = "8928308280fffff"
        geojson = h3_to_boundary_geojson(h3_idx)
        assert geojson["type"] == "Polygon"
        assert len(geojson["coordinates"][0]) >= 7  # 6 coordinates + closed point

    def test_geojson_centroid_point(self):
        geom = {"type": "Point", "coordinates": [36.8219, -1.2921]}
        lat, lng = geojson_centroid(geom)
        assert lat == -1.2921
        assert lng == 36.8219

    def test_geojson_centroid_polygon(self):
        geom = {
            "type": "Polygon",
            "coordinates": [
                [
                    [36.8, -1.3],
                    [36.9, -1.3],
                    [36.9, -1.2],
                    [36.8, -1.2],
                    [36.8, -1.3]
                ]
            ]
        }
        lat, lng = geojson_centroid(geom)
        assert pytest.approx(lat) == -1.26
        assert pytest.approx(lng) == 36.84



@pytest.mark.django_db
class TestGeospatialModels:
    def test_create_h3_grid_and_risk(self):
        grid = H3Grid.objects.create(
            resolution=9,
            h3_index="8928308280fffff",
            centroid_lat=Decimal("-1.292100"),
            centroid_lng=Decimal("36.821900")
        )
        assert grid.id is not None
        assert H3Grid.objects.filter(h3_index="8928308280fffff").exists()

        risk = GridRisk.objects.create(
            h3_index="8928308280fffff",
            mean_rainfall_mm=Decimal("1200.50"),
            flood_threshold_mm=Decimal("50.00"),
            drought_risk_score=Decimal("0.1234"),
            flood_risk_score=Decimal("0.0543")
        )
        assert risk.id is not None
        assert GridRisk.objects.filter(h3_index="8928308280fffff").exists()
