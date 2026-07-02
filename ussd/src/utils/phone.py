"""Phone number formatting utilities."""

from __future__ import annotations

import re

KENYAN_PHONE_PATTERN = re.compile(r"^254[17]\d{8}$")


def normalize_phone(phone: str) -> str:
	"""Normalize a Kenyan phone number to 254XXXXXXXXX format."""
	digits = "".join(ch for ch in phone if ch.isdigit())
	if digits.startswith("0") and len(digits) == 10:
		digits = f"254{digits[1:]}"
	elif digits.startswith("7") and len(digits) == 9:
		digits = f"254{digits}"
	elif digits.startswith("1") and len(digits) == 9:
		digits = f"254{digits}"
	elif not digits.startswith("254"):
		digits = f"254{digits}"
	return digits


def is_valid_kenyan_phone(phone: str) -> bool:
	return bool(KENYAN_PHONE_PATTERN.match(normalize_phone(phone)))


def mask_phone(phone: str) -> str:
	normalized = normalize_phone(phone)
	return f"{normalized[:6]}***{normalized[-3:]}"
