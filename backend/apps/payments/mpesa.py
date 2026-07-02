"""M-Pesa payment client (app layer)."""

from __future__ import annotations

from integrations.mpesa import MpesaClient


def get_mpesa_client() -> MpesaClient:
	return MpesaClient()
