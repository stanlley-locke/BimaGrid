"""ArdhiSasa land registry client."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ArdhiSasaClient:
	def __init__(self) -> None:
		self.api_url = settings.ARDHISASA_API_URL.rstrip("/")
		self.client_id = settings.ARDHISASA_CLIENT_ID
		self.client_secret = settings.ARDHISASA_CLIENT_SECRET
		self.use_mock = settings.ARDHISASA_USE_MOCK
		self._token: str | None = None

	def _get_token(self) -> str:
		if self.use_mock:
			return "mock-ardhisasa-token"
		if self._token:
			return self._token
		response = requests.post(
			f"{self.api_url}/oauth/token",
			data={
				"grant_type": "client_credentials",
				"client_id": self.client_id,
				"client_secret": self.client_secret,
			},
			timeout=30,
		)
		response.raise_for_status()
		self._token = response.json()["access_token"]
		return self._token

	def verify_title(
		self,
		title_number: str,
		owner_id_number: str,
		parcel_number: str,
	) -> dict[str, Any]:
		if self.use_mock:
			logger.info("Mock ArdhiSasa verify title %s for %s", title_number, owner_id_number)
			return {
				"status": "verified",
				"title_details": {
					"title_number": title_number,
					"parcel_number": parcel_number,
					"owner_id": owner_id_number,
					"land_area_hectares": 2.5,
					"land_use": "Agricultural",
					"encumbrances": [],
					"status": "ACTIVE",
				},
			}

		response = requests.post(
			f"{self.api_url}/title/verify",
			json={
				"title_number": title_number,
				"owner_id_number": owner_id_number,
				"parcel_number": parcel_number,
			},
			headers={"Authorization": f"Bearer {self._get_token()}"},
			timeout=30,
		)
		response.raise_for_status()
		return response.json()
