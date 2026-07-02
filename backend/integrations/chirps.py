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
	except requests.RequestException as exc:
		logger.warning("CHIRPS API unavailable, using mock: %s", exc)

	seed = int(hashlib.sha256(f"{lat:.3f}{lon:.3f}".encode()).hexdigest()[:8], 16)
	days = (end_date - start_date).days + 1
	data = []
	for offset in range(days):
		current = start_date.toordinal() + offset
		precip = round(5 + (seed + current) % 40 + ((seed >> 4) % 10) / 10, 1)
		data.append({"date": date.fromordinal(current).isoformat(), "precipitation": precip})
	return {"location": {"lat": lat, "lon": lon}, "data": data, "source": "mock"}
