"""Import historical weather-derived grid risk scores."""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.geospatial.h3_utils import h3_to_lat_lng
from apps.geospatial.models import GridRisk, H3Grid
from integrations.chirps import fetch_chirps_daily
from integrations.nasa_power import fetch_nasa_power_daily


class Command(BaseCommand):
	help = "Import historical weather data and compute grid risk scores for loaded H3 cells."

	def add_arguments(self, parser):
		parser.add_argument("--limit", type=int, default=100, help="Max cells to process")

	def handle(self, *args, **options):
		limit = options["limit"]
		end = date.today()
		start = end - timedelta(days=365 * 5)
		count = 0
		for grid in H3Grid.objects.all()[:limit]:
			lat = float(grid.centroid_lat)
			lng = float(grid.centroid_lng)
			chirps = fetch_chirps_daily(lat, lng, start, end)
			nasa = fetch_nasa_power_daily(lat, lng, start, end)
			precip_values = [row["precipitation"] for row in chirps.get("data", [])]
			mean_rainfall = sum(precip_values) / len(precip_values) if precip_values else 50.0
			t2m = nasa.get("parameters", {}).get("T2M", {})
			frost_days = sum(1 for value in t2m.values() if isinstance(value, (int, float)) and value < 2)
			heat_days = sum(1 for value in t2m.values() if isinstance(value, (int, float)) and value > 35)
			seed = int(hashlib.sha256(grid.h3_index.encode()).hexdigest()[:8], 16)
			drought_score = Decimal(str(min(1.0, max(0.1, 1.0 - mean_rainfall / 120)))).quantize(Decimal("0.0001"))
			flood_score = Decimal(str(min(1.0, max(0.1, mean_rainfall / 200)))).quantize(Decimal("0.0001"))
			GridRisk.objects.update_or_create(
				h3_index=grid.h3_index,
				defaults={
					"mean_rainfall_mm": Decimal(str(round(mean_rainfall, 2))),
					"flood_threshold_mm": Decimal(str(round(mean_rainfall * 1.8, 2))),
					"frost_days": frost_days,
					"heat_stress_days": heat_days,
					"drought_risk_score": drought_score,
					"flood_risk_score": flood_score,
					"metadata": {
						"chirps_source": chirps.get("source", "api"),
						"nasa_source": nasa.get("header", {}).get("source", "api"),
						"seed": seed,
						"centroid": {"lat": lat, "lng": lng},
					},
				},
			)
			count += 1
		if count == 0:
			self.stdout.write(self.style.WARNING("No H3 grids found. Run load_h3_grids first."))
		else:
			self.stdout.write(self.style.SUCCESS(f"Imported weather risk for {count} grid cells"))
