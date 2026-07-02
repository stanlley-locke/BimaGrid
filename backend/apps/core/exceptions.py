"""Custom application exceptions."""

from __future__ import annotations


class BimaGridError(Exception):
	"""Base exception for BimaGrid backend errors."""

	code = "INTERNAL_ERROR"
	status_code = 500

	def __init__(self, message: str, *, details: dict | None = None):
		super().__init__(message)
		self.message = message
		self.details = details or {}


class ValidationError(BimaGridError):
	code = "VALIDATION_ERROR"
	status_code = 400


class ExternalAPIError(BimaGridError):
	code = "EXTERNAL_API_ERROR"
	status_code = 502


class MpesaError(ExternalAPIError):
	code = "MPESA_ERROR"


class OracleSignatureError(BimaGridError):
	code = "ORACLE_SIGNATURE_INVALID"
	status_code = 401


class NotFoundError(BimaGridError):
	code = "NOT_FOUND"
	status_code = 404
