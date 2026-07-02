"""Registration flow input validators."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from src.utils.constants import CROP_MENU
from src.utils.phone import is_valid_kenyan_phone, normalize_phone


def validate_ward_code(value: str) -> tuple[bool, str]:
	ward = value.strip()
	if len(ward) == 4 and ward.isdigit():
		return True, ward
	return False, ward


def validate_crop_choice(value: str) -> tuple[bool, str, str]:
	crop_entry = CROP_MENU.get(value.strip())
	if not crop_entry:
		return False, "", ""
	crop_code, crop_label = crop_entry
	return True, crop_code, crop_label


def validate_acreage(value: str) -> tuple[bool, Decimal | None]:
	try:
		acreage = Decimal(value.strip())
		if acreage <= 0:
			return False, None
		return True, acreage
	except (InvalidOperation, ValueError):
		return False, None


def validate_mpesa_choice(choice: str, phone: str, custom_number: str = "") -> tuple[bool, str]:
	if choice.strip() == "1":
		return True, phone
	if choice.strip() == "2":
		if not custom_number:
			return False, ""
		normalized = normalize_phone(custom_number)
		if is_valid_kenyan_phone(normalized):
			return True, normalized
		return False, normalized
	# Direct number entry when user chose option 2 on previous screen
	normalized = normalize_phone(choice)
	if is_valid_kenyan_phone(normalized):
		return True, normalized
	return False, normalized
