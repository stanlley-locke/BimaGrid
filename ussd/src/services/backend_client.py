"""HTTP client for the BimaGrid Django backend."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class BackendAPIError(Exception):
	def __init__(self, message: str, status_code: int | None = None, payload: Any = None) -> None:
		super().__init__(message)
		self.status_code = status_code
		self.payload = payload


class BackendAPIClient:
	"""Client for USSD internal backend endpoints."""

	def __init__(
		self,
		base_url: str | None = None,
		api_key: str | None = None,
		timeout: float | None = None,
	) -> None:
		self.base_url = (base_url or settings.BACKEND_URL).rstrip("/")
		self.api_key = api_key or settings.BACKEND_API_KEY
		self.timeout = timeout or settings.BACKEND_TIMEOUT_SECONDS

	def _headers(self) -> dict[str, str]:
		return {
			"Content-Type": "application/json",
			"Accept": "application/json",
			"X-USSD-Internal-Key": self.api_key,
		}

	def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
		url = f"{self.base_url}{path}"
		import time
		for attempt in range(3):
			try:
				with httpx.Client(timeout=self.timeout) as client:
					response = client.request(method, url, headers=self._headers(), **kwargs)
					break
			except httpx.RequestError as exc:
				if attempt == 2:
					logger.exception("Backend request failed after retries: %s %s", method, url)
					raise BackendAPIError(f"Backend unavailable: {exc}") from exc
				time.sleep(2 ** attempt)

		if response.status_code >= 400:
			payload: Any
			try:
				payload = response.json()
			except ValueError:
				payload = response.text
			raise BackendAPIError(
				f"Backend error ({response.status_code})",
				status_code=response.status_code,
				payload=payload,
			)

		if not response.content:
			return {}
		return response.json()

	def health(self) -> dict[str, Any]:
		with httpx.Client(timeout=self.timeout) as client:
			response = client.get(f"{self.base_url}/health/")
			response.raise_for_status()
			return response.json()

	def register_farmer(
		self,
		phone: str,
		ward_code: str,
		crop: str,
		acreage: str | float,
		mpesa_number: str,
	) -> dict[str, Any]:
		return self._request(
			"POST",
			"/api/v1/ussd/internal/register/",
			json={
				"phone": phone,
				"ward_code": ward_code,
				"crop": crop,
				"acreage": str(acreage),
				"mpesa_number": mpesa_number,
			},
		)

	def get_policy_status(self, phone: str) -> dict[str, Any]:
		return self._request(
			"GET",
			"/api/v1/ussd/internal/policy-status/",
			params={"phone": phone},
		)

	def file_claim(self, phone: str, loss_type: str = "drought", description: str = "") -> dict[str, Any]:
		return self._request(
			"POST",
			"/api/v1/ussd/internal/claim/",
			json={
				"phone": phone,
				"loss_type": loss_type,
				"description": description,
			},
		)


_default_client: BackendAPIClient | None = None


def get_backend_client() -> BackendAPIClient:
	global _default_client
	if _default_client is None:
		_default_client = BackendAPIClient()
	return _default_client
