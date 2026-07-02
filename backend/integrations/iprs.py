"""IPRS identity verification client."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class IPRSClient:
	def __init__(self) -> None:
		self.api_url = settings.IPRS_API_URL.rstrip("/")
		self.api_key = settings.IPRS_API_KEY
		self.use_mock = settings.IPRS_USE_MOCK

	def verify_identity(
		self,
		id_number: str,
		first_name: str,
		last_name: str,
		date_of_birth: str,
	) -> dict[str, Any]:
		if self.use_mock:
			digest = hashlib.sha256(f"{id_number}{first_name}{last_name}".encode()).hexdigest()
			verified = digest[-1] in "02468ace"
			logger.info("Mock IPRS verify %s -> %s", id_number, "verified" if verified else "partial_match")
			return {
				"status": "verified" if verified else "partial_match",
				"confidence_score": 0.98 if verified else 0.72,
				"details": {
					"id_number": id_number,
					"full_name": f"{first_name} {last_name}",
					"date_of_birth": date_of_birth,
					"gender": "M",
					"status": "ACTIVE",
				},
			}

		response = requests.post(
			f"{self.api_url}/identity/verify",
			json={
				"id_number": id_number,
				"first_name": first_name,
				"last_name": last_name,
				"date_of_birth": date_of_birth,
			},
			headers={"X-API-Key": self.api_key},
			timeout=30,
		)
		response.raise_for_status()
		return response.json()
