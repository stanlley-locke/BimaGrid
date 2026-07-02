"""Registration flow screen text."""

from __future__ import annotations

from src.screens import templates as screens

__all__ = [
	"acreage_prompt",
	"crop_selection_prompt",
	"invalid_acreage_prompt",
	"invalid_crop_prompt",
	"invalid_mpesa_prompt",
	"invalid_ward_code_prompt",
	"mpesa_confirm_prompt",
	"registration_complete",
	"ward_code_prompt",
]

acreage_prompt = screens.acreage_prompt
crop_selection_prompt = screens.crop_selection_prompt
invalid_acreage_prompt = screens.invalid_acreage_prompt
invalid_crop_prompt = screens.invalid_crop_prompt
invalid_mpesa_prompt = screens.invalid_mpesa_prompt
invalid_ward_code_prompt = screens.invalid_ward_code_prompt
mpesa_confirm_prompt = screens.mpesa_confirm_prompt
registration_complete = screens.registration_complete
ward_code_prompt = screens.ward_code_prompt
