"""Shared USSD constants."""

from __future__ import annotations

CROP_MENU: dict[str, tuple[str, str]] = {
	"1": ("maize", "Maize"),
	"2": ("beans", "Beans"),
	"3": ("wheat", "Wheat"),
	"4": ("rice", "Rice"),
}

MAIN_MENU_OPTIONS = {
	"1": "registration",
	"2": "policy_status",
	"3": "claims",
}

SERVICE_CODE = "*384*123#"
