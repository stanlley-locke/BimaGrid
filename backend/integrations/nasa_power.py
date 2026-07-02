"""NASA POWER meteorological data client."""

from __future__ import annotations

import hashlib
import logging
from datetime import date
from typing import Any

import requests

logger = logging.getLogger(__name__)

NASA_POWER_URL = "https://power.larc.nasa.gov/api/point/daily/historical"


def fetch_nasa_power_daily(
	lat: float,
	lon: float,
	start_date: date,
	end_date: date,
	parameters: str = "T2M,T2M_MAX,T2M_MIN,PRECTOT",
) -> dict[str, Any]:
	try:
		response = requests.get(
			NASA_POWER_URL,
			params={
				"parameters": parameters,
				"community": "AG",
				"longitude": lon,
				"latitude": lat,
				"start": start_date.strftime("%Y%m%d"),
				"end": end_date.strftime("%Y%m%d"),
				"format": "JSON",
			},
			timeout=20,
		)
		if response.ok:
			return response.json()
	except requests.RequestException as exc:
		logger.warning("NASA POWER unavailable, using mock: %s", exc)

	seed = int(hashlib.sha256(f"{lat:.3f}{lon:.3f}".encode()).hexdigest()[:8], 16)
	parameters_data: dict[str, dict[str, float]] = {"T2M": {}, "T2M_MAX": {}, "T2M_MIN": {}, "PRECTOT": {}}
	current = start_date
	while current <= end_date:
		key = current.strftime("%Y%m%d")
		base = 18 + (seed + current.toordinal()) % 12
		parameters_data["T2M"][key] = float(base)
		parameters_data["T2M_MAX"][key] = float(base + 6)
		parameters_data["T2M_MIN"][key] = float(base - 4)
		parameters_data["PRECTOT"][key] = float((seed + current.day) % 25)
		current = date.fromordinal(current.toordinal() + 1)
	return {
		"parameters": parameters_data,
		"header": {"title": "Mock NASA POWER", "source": "mock"},
	}
