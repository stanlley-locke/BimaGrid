"""Load H3 grid cells for a region."""

from __future__ import annotations

import h3
from django.core.management.base import BaseCommand

from apps.geospatial.h3_utils import polyfill_geojson
from apps.geospatial.services import ensure_h3_grid


class Command(BaseCommand):
	help = "Load H3 grid cells at the given resolution (default 9) for the Nairobi demo region."

	def add_arguments(self, parser):
		parser.add_argument("--resolution", type=int, default=9)
		parser.add_argument("--region-code", type=str, default="NBI")

	def handle(self, *args, **options):
		resolution = options["resolution"]
		region_code = options["region_code"]
		geojson = {
			"type": "Polygon",
			"coordinates": [
				[
					[36.70, -1.40],
					[37.00, -1.40],
					[37.00, -1.15],
					[36.70, -1.15],
					[36.70, -1.40],
				]
			],
		}
		cells = polyfill_geojson(geojson, resolution)
		count = 0
		for cell in cells:
			ensure_h3_grid(cell, resolution=resolution, region_code=region_code)
			count += 1
		self.stdout.write(self.style.SUCCESS(f"Loaded {count} H3 cells at resolution {resolution}"))
