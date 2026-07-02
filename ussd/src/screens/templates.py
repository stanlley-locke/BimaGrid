"""USSD screen rendering helpers."""

from __future__ import annotations


def con(message: str) -> str:
	"""Build a continue (CON) USSD response."""
	return f"CON {message.strip()}"


def end(message: str) -> str:
	"""Build a terminate (END) USSD response."""
	return f"END {message.strip()}"


def welcome_menu() -> str:
	return con("Welcome to BimaGrid.\n1. Register Farm\n2. Check Policy Status\n3. File Claim")


def ward_code_prompt() -> str:
	return con("Enter your 4-digit Ward Code:")


def invalid_ward_code_prompt() -> str:
	return con("Invalid ward code. Enter 4 digits:")


def crop_selection_prompt() -> str:
	return con("Select crop:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice")


def invalid_crop_prompt() -> str:
	return con("Invalid crop. Select:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice")


def acreage_prompt() -> str:
	return con("Enter acreage (e.g. 2.5):")


def invalid_acreage_prompt() -> str:
	return con("Invalid acreage. Enter a number (e.g. 2.5):")


def mpesa_confirm_prompt(phone: str) -> str:
	return con(f"Confirm M-Pesa number:\n1. Use {phone}\n2. Enter different number")


def invalid_mpesa_prompt() -> str:
	return con("Invalid M-Pesa number. Enter 254XXXXXXXXX:")


def registration_complete(data: dict) -> str:
	return end(
		"Registration complete.\n"
		f"Ward: {data.get('ward_code', '')}\n"
		f"Crop: {data.get('crop_label', data.get('crop', ''))}\n"
		f"Acreage: {data.get('acreage', '')}\n"
		f"{data.get('message', 'Premium quote pending agent review.')}"
	)


def policy_status_message(data: dict) -> str:
	status = data.get("status", "unknown")
	if status == "not_found":
		return end(data.get("message", "No BimaGrid account found. Dial again and choose 1 to register."))
	if status == "incomplete":
		return end(data.get("message", "Registration incomplete. Choose 1 to register your farm."))
	if status == "no_policy":
		return end(data.get("message", "No policy issued yet."))
	return end(
		f"Policy {data.get('policy_number', '')}\n"
		f"Crop: {data.get('crop', '')}\n"
		f"Status: {str(data.get('policy_status', '')).upper()}\n"
		f"Premium: KES {data.get('premium_amount', '')}"
	)


def claim_message(data: dict) -> str:
	return end(data.get("message", "Parametric claims are automatic when drought is detected."))


def invalid_option() -> str:
	return end("Invalid option. Dial again to restart.")


def session_expired() -> str:
	return end("Session expired. Dial again to restart.")


def backend_error_message() -> str:
	return end("Service temporarily unavailable. Please try again later.")
