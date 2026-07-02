"""M-Pesa Daraja API client."""

from __future__ import annotations

import base64
import logging
from datetime import datetime
from typing import Any

import requests
from django.conf import settings

from apps.core.exceptions import MpesaError

logger = logging.getLogger(__name__)


class MpesaClient:
	def __init__(self) -> None:
		self.consumer_key = settings.MPESA_CONSUMER_KEY
		self.consumer_secret = settings.MPESA_CONSUMER_SECRET
		self.shortcode = settings.MPESA_SHORTCODE
		self.passkey = settings.MPESA_PASSKEY
		self.initiator_name = settings.MPESA_INITIATOR_NAME
		self.security_credential = settings.MPESA_SECURITY_CREDENTIAL
		self.b2c_shortcode = settings.MPESA_B2C_SHORTCODE
		self.callback_base = settings.MPESA_CALLBACK_BASE_URL.rstrip("/")
		self.use_mock = settings.MPESA_USE_MOCK
		self.base_url = (
			"https://sandbox.safaricom.co.ke"
			if settings.MPESA_ENVIRONMENT == "sandbox"
			else "https://api.safaricom.co.ke"
		)
		self._access_token: str | None = None

	def _get_access_token(self) -> str:
		if self.use_mock:
			return "mock-access-token"
		if self._access_token:
			return self._access_token
		credentials = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
		response = requests.get(
			f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
			headers={"Authorization": f"Basic {credentials}"},
			timeout=30,
		)
		response.raise_for_status()
		self._access_token = response.json()["access_token"]
		return self._access_token

	def _stk_password(self) -> tuple[str, str]:
		timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
		password = base64.b64encode(f"{self.shortcode}{self.passkey}{timestamp}".encode()).decode()
		return timestamp, password

	def stk_push(
		self,
		phone_number: str,
		amount: float,
		account_reference: str,
		transaction_desc: str = "BimaGrid Premium Payment",
	) -> dict[str, Any]:
		if self.use_mock:
			checkout_id = f"ws_CO_MOCK_{account_reference}"
			logger.info("Mock STK push %s KES %s to %s", account_reference, amount, phone_number)
			return {
				"MerchantRequestID": f"MOCK-MR-{account_reference}",
				"CheckoutRequestID": checkout_id,
				"ResponseCode": "0",
				"ResponseDescription": "Success. Request accepted for processing",
				"CustomerMessage": "Success. Request accepted for processing",
			}

		timestamp, password = self._stk_password()
		payload = {
			"BusinessShortCode": self.shortcode,
			"Password": password,
			"Timestamp": timestamp,
			"TransactionType": "CustomerPayBillOnline",
			"Amount": str(int(amount)),
			"PartyA": phone_number,
			"PartyB": self.shortcode,
			"PhoneNumber": phone_number,
			"CallBackURL": f"{self.callback_base}/api/payments/mpesa/callback/",
			"AccountReference": account_reference,
			"TransactionDesc": transaction_desc,
		}
		response = requests.post(
			f"{self.base_url}/mpesa/stkpush/v1/processrequest",
			json=payload,
			headers={"Authorization": f"Bearer {self._get_access_token()}"},
			timeout=30,
		)
		if not response.ok:
			raise MpesaError(f"STK push failed: {response.text}")
		return response.json()

	def b2c_payout(
		self,
		phone_number: str,
		amount: float,
		occasion: str = "",
		remarks: str = "BimaGrid payout",
	) -> dict[str, Any]:
		if self.use_mock:
			logger.info("Mock B2C payout KES %s to %s (%s)", amount, phone_number, occasion)
			return {
				"ConversationID": f"AG_MOCK_{phone_number[-4:]}",
				"OriginatorConversationID": f"MOCK-ORIG-{occasion or 'payout'}",
				"ResponseDescription": "Accept the service request successfully.",
			}

		payload = {
			"InitiatorName": self.initiator_name,
			"SecurityCredential": self.security_credential,
			"CommandID": "BusinessPayment",
			"Amount": str(int(amount)),
			"PartyA": self.b2c_shortcode,
			"PartyB": phone_number,
			"Remarks": remarks,
			"QueueTimeOutURL": f"{self.callback_base}/api/payments/mpesa/timeout/",
			"ResultURL": f"{self.callback_base}/api/payments/mpesa/result/",
			"Occasion": occasion,
		}
		response = requests.post(
			f"{self.base_url}/mpesa/b2c/v1/paymentrequest",
			json=payload,
			headers={"Authorization": f"Bearer {self._get_access_token()}"},
			timeout=30,
		)
		if not response.ok:
			raise MpesaError(f"B2C payout failed: {response.text}")
		return response.json()

	def stk_push_query(self, checkout_request_id: str) -> dict[str, Any]:
		if self.use_mock:
			return {
				"ResponseCode": "0",
				"ResponseDescription": "The service request has been accepted successfully.",
				"ResultCode": "0",
				"ResultDesc": "The service request is processed successfully.",
				"CheckoutRequestID": checkout_request_id,
			}

		timestamp, password = self._stk_password()
		payload = {
			"BusinessShortCode": self.shortcode,
			"Password": password,
			"Timestamp": timestamp,
			"CheckoutRequestID": checkout_request_id,
		}
		response = requests.post(
			f"{self.base_url}/mpesa/stkpushquery/v1/query",
			json=payload,
			headers={"Authorization": f"Bearer {self._get_access_token()}"},
			timeout=30,
		)
		if not response.ok:
			raise MpesaError(f"STK push query failed: {response.text}")
		return response.json()
