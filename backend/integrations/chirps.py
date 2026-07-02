"""CHIRPS rainfall data client."""

from __future__ import annotations

import hashlib
import logging
from datetime import date
from typing import Any

import requests

logger = logging.getLogger(__name__)

CHIRPS_API_URL = "https://chcdata.org/api/chirps/daily"


def fetch_chirps_daily(lat: float, lon: float, start_date: date, end_date: date) -> dict[str, Any]:
	"""Fetch daily precipitation from CHIRPS API or return mock data."""
	import time
	for attempt in range(3):
		try:
			response = requests.get(
				CHIRPS_API_URL,
				params={
					"lat": lat,
					"lon": lon,
					"start_date": start_date.isoformat(),
					"end_date": end_date.isoformat(),
				},
				timeout=15,
			)
			if response.ok:
				return response.json()
			if response.status_code == 429 and attempt < 2:
				time.sleep(2 ** attempt)
				continue
			break
		except requests.RequestException as exc:
			if attempt == 2:
				logger.warning("CHIRPS API unavailable after retries, using mock: %s", exc)
			else:
				time.sleep(2 ** attempt)

	seed = int(hashlib.sha256(f"{lat:.3f}{lon:.3f}".encode()).hexdigest()[:8], 16)
	days = (end_date - start_date).days + 1
	data = []
	for offset in range(days):
		current = start_date.toordinal() + offset
		precip = round(5 + (seed + current) % 40 + ((seed >> 4) % 10) / 10, 1)
		data.append({"date": date.fromordinal(current).isoformat(), "precipitation": precip})
	return {"location": {"lat": lat, "lon": lon}, "data": data, "source": "mock"}
