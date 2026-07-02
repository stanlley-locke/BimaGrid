"""openEO client for satellite app."""

from __future__ import annotations

from integrations.openeo import OpenEOClient


def get_openeo_client() -> OpenEOClient:
	return OpenEOClient()
