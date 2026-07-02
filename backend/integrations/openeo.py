"""openEO satellite processing client."""

from __future__ import annotations

import hashlib
import logging
from datetime import date
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenEOClient:
	def __init__(self) -> None:
		self.backend_url = settings.OPENEO_BACKEND_URL.rstrip("/")
		self.username = settings.OPENEO_USERNAME
		self.password = settings.OPENEO_PASSWORD
		self.use_mock = settings.OPENEO_USE_MOCK

	def _mock_index(self, h3_index: str, index_name: str) -> float:
		seed = int(hashlib.sha256(f"{h3_index}:{index_name}".encode()).hexdigest()[:8], 16)
		if index_name == "ndvi":
			return round(0.2 + (seed % 6000) / 10000, 4)
		if index_name == "ndwi":
			return round(-0.1 + (seed % 5000) / 10000, 4)
		if index_name == "evi":
			return round(0.15 + (seed % 5500) / 10000, 4)
		return round((seed % 10000) / 10000, 4)

	def compute_index(
		self,
		h3_index: str,
		index_name: str,
		spatial_extent: dict[str, float] | None = None,
		temporal_extent: tuple[date, date] | None = None,
	) -> dict[str, Any]:
		if self.use_mock:
			value = self._mock_index(h3_index, index_name)
			logger.info("Mock openEO %s for %s = %s", index_name, h3_index, value)
			return {
				"h3_index": h3_index,
				"index": index_name,
				"mean": value,
				"source": "mock-openeo",
				"spatial_extent": spatial_extent,
				"temporal_extent": [d.isoformat() for d in temporal_extent] if temporal_extent else None,
			}

		process_graph = {
			"process_graph": {
				"load": {
					"process_id": "load_collection",
					"arguments": {
						"id": "SENTINEL2_L2A",
						"spatial_extent": spatial_extent,
						"temporal_extent": [d.isoformat() for d in temporal_extent] if temporal_extent else None,
						"bands": ["B03", "B04", "B08"],
					},
				},
			}
		}
		response = requests.post(
			f"{self.backend_url}/result",
			json=process_graph,
			auth=(self.username, self.password),
			timeout=60,
		)
		response.raise_for_status()
		result = response.json()
		result["h3_index"] = h3_index
		result["index"] = index_name
		return result

	def compute_ndvi(self, h3_index: str, spatial_extent: dict[str, float]) -> dict[str, Any]:
		return self.compute_index(h3_index, "ndvi", spatial_extent=spatial_extent)

	def compute_ndwi(self, h3_index: str, spatial_extent: dict[str, float]) -> dict[str, Any]:
		return self.compute_index(h3_index, "ndwi", spatial_extent=spatial_extent)

	def compute_evi(self, h3_index: str, spatial_extent: dict[str, float]) -> dict[str, Any]:
		return self.compute_index(h3_index, "evi", spatial_extent=spatial_extent)
