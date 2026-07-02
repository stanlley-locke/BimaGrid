"""Blockchain JSON-RPC client."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class BlockchainClient:
	def __init__(self) -> None:
		self.rpc_url = settings.BLOCKCHAIN_RPC_URL.rstrip("/")

	def call(self, method: str, params: list | None = None) -> Any:
		try:
			response = requests.post(
				self.rpc_url,
				json={"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1},
				timeout=10,
			)
			response.raise_for_status()
			payload = response.json()
			if "error" in payload:
				logger.warning("Blockchain RPC error: %s", payload["error"])
				return None
			return payload.get("result")
		except requests.RequestException as exc:
			logger.warning("Blockchain RPC unavailable: %s", exc)
			return None

	def get_transaction_receipt(self, tx_hash: str) -> dict[str, Any] | None:
		return self.call("eth_getTransactionReceipt", [tx_hash])

	def send_raw_transaction(self, raw_tx: str) -> str | None:
		return self.call("eth_sendRawTransaction", [raw_tx])
