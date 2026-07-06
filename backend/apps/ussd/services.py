"""USSD session flow logic for Africa's Talking gateway."""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile
from apps.geospatial.tasks import profile_ward_area
from apps.onboarding.constants import CropChoice
from apps.onboarding.services import get_or_create_onboarding, submit_onboarding
from apps.policies.models import Policy

from .geography_flow import (
	county_prompt,
	county_selected,
	constituency_prompt,
	constituency_selected,
	geography_data_loaded,
	resolve_ward,
	subcounty_prompt,
	subcounty_selected,
	ward_prompt,
	ward_selected,
)

User = get_user_model()
logger = logging.getLogger(__name__)

CROP_MENU = {
	"1": CropChoice.MAIZE,
	"2": CropChoice.BEANS,
	"3": CropChoice.WHEAT,
	"4": CropChoice.RICE,
}


def normalize_phone(phone: str) -> str:
	digits = "".join(ch for ch in phone if ch.isdigit())
	if digits.startswith("0"):
		digits = f"254{digits[1:]}"
	elif not digits.startswith("254"):
		digits = f"254{digits}"
	return digits


def get_or_create_farmer_profile(phone: str) -> Profile:
	username = f"ussd_{phone[-9:]}"
	user, created = User.objects.get_or_create(
		username=username,
		defaults={"email": f"{username}@ussd.bimagrid.local"},
	)
	if created:
		user.set_unusable_password()
		user.save(update_fields=["password"])
	profile, _ = Profile.objects.get_or_create(
		user=user,
		defaults={
			"phone_number": phone,
			"full_name": f"Farmer {phone[-4:]}",
			"role": Profile.Role.FARMER,
		},
	)
	if profile.phone_number != phone:
		profile.phone_number = phone
		profile.save(update_fields=["phone_number", "updated_at"])
	return profile


def policy_status_text(phone: str) -> str:
	profile = Profile.objects.filter(phone_number=phone).first()
	if not profile:
		return "END No BimaGrid account found. Dial again and choose 1 to register."
	onboarding = getattr(profile, "onboarding", None)
	if not onboarding:
		return "END Registration incomplete. Choose 1 to register your farm."
	policy = Policy.objects.filter(onboarding=onboarding).order_by("-created_at").first()
	if not policy:
		return f"END Onboarding {onboarding.status}. No policy issued yet."
	return (
		f"END Policy {policy.policy_number}\n"
		f"Crop: {policy.crop}\n"
		f"Status: {policy.status.upper()}\n"
		f"Premium: KES {policy.premium_amount}"
	)


def proxy_to_standalone_ussd(session_id: str, phone: str, text: str) -> str | None:
	"""Forward USSD session to standalone service when USSD_SERVICE_URL is set."""
	base_url = getattr(settings, "USSD_SERVICE_URL", "").rstrip("/")
	if not base_url:
		return None
	try:
		response = requests.post(
			f"{base_url}/ussd/gateway/",
			data={
				"sessionId": session_id,
				"phoneNumber": phone,
				"text": text,
			},
			timeout=10,
		)
		response.raise_for_status()
		return response.text
	except requests.RequestException as exc:
		logger.warning("USSD proxy failed: %s", exc)
		return "END Service temporarily unavailable. Please try again later."


def _finalize_registration(phone: str, ward_external_id: str, crop_key: str, acreage: Decimal, mpesa: str) -> str:
	ward = resolve_ward(ward_external_id)
	profile = get_or_create_farmer_profile(phone)
	onboarding = get_or_create_onboarding(profile)
	onboarding.ward = ward
	onboarding.ward_code = ward.ward_code if ward else ward_external_id.zfill(4)
	onboarding.crop = CROP_MENU[crop_key]
	onboarding.acreage = acreage
	onboarding.mpesa_number = mpesa
	onboarding.save(
		update_fields=["ward", "ward_code", "crop", "acreage", "mpesa_number", "updated_at"]
	)
	submit_onboarding(onboarding)
	if ward:
		profile_ward_area.delay(str(ward.id))
	ward_label = ward.name if ward else onboarding.ward_code
	return (
		f"END Registration complete.\n"
		f"Ward: {ward_label}\n"
		f"Crop: {onboarding.crop}\n"
		f"Acreage: {onboarding.acreage}\n"
		f"Premium quote pending agent review."
	)


def _handle_hierarchical_registration(steps: list[str], phone: str) -> str:
	depth = len(steps)

	if depth == 1:
		return county_prompt([])

	if depth == 2:
		county_id = county_selected([steps[1]])
		if county_id:
			return subcounty_prompt(county_id, [])
		return county_prompt([steps[1]])

	county_id = county_selected([steps[1]])
	if not county_id:
		return county_prompt([steps[1]])

	if depth == 3:
		subcounty_id = subcounty_selected(county_id, [steps[2]])
		if subcounty_id:
			return constituency_prompt(subcounty_id, [])
		return subcounty_prompt(county_id, [steps[2]])

	subcounty_id = subcounty_selected(county_id, [steps[2]])
	if not subcounty_id:
		return subcounty_prompt(county_id, [steps[2]])

	if depth == 4:
		constituency_id = constituency_selected(subcounty_id, [steps[3]])
		if constituency_id:
			return ward_prompt(constituency_id, [])
		return constituency_prompt(subcounty_id, [steps[3]])

	constituency_id = constituency_selected(subcounty_id, [steps[3]])
	if not constituency_id:
		return constituency_prompt(subcounty_id, [steps[3]])

	if depth == 5:
		ward_id = ward_selected(constituency_id, [steps[4]])
		if ward_id:
			return "CON Select crop:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice"
		return ward_prompt(constituency_id, [steps[4]])

	ward_id = ward_selected(constituency_id, [steps[4]])
	if not ward_id:
		return ward_prompt(constituency_id, [steps[4]])

	if depth == 6:
		if steps[5] not in CROP_MENU:
			return "CON Invalid crop. Select:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice"
		return "CON Enter acreage (e.g. 2.5):"

	if depth == 7:
		try:
			acreage = Decimal(steps[6])
			if acreage <= 0:
				raise InvalidOperation
		except (InvalidOperation, ValueError):
			return "CON Invalid acreage. Enter a number (e.g. 2.5):"
		return f"CON Confirm M-Pesa number:\n1. Use {phone}\n2. Enter different number"

	if depth == 8:
		mpesa = phone if steps[7] == "1" else normalize_phone(steps[7])
		return _finalize_registration(phone, ward_id, steps[5], Decimal(steps[6]), mpesa)

	return "END Session expired. Dial again to restart."


def handle_ussd_session(session_id: str, phone: str, text: str) -> str:
	"""Process cumulative USSD input and return CON/END response."""
	proxied = proxy_to_standalone_ussd(session_id, phone, text)
	if proxied is not None:
		return proxied

	phone = normalize_phone(phone)
	steps = text.split("*") if text else []

	if not steps or steps[0] == "":
		return "CON Welcome to BimaGrid.\n1. Register Farm\n2. Check Policy Status\n3. File Claim"

	choice = steps[0]
	if choice == "2":
		return policy_status_text(phone)

	if choice == "3":
		return "END Parametric claims are automatic. No manual filing needed when drought is detected."

	if choice != "1":
		return "END Invalid option. Dial again to restart."

	if geography_data_loaded():
		return _handle_hierarchical_registration(steps, phone)

	if len(steps) == 1:
		return "CON Enter your 4-digit Ward Code:"

	if len(steps) == 2:
		ward = steps[1].strip()
		if len(ward) != 4 or not ward.isdigit():
			return "CON Invalid ward code. Enter 4 digits:"
		return "CON Select crop:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice"

	if len(steps) == 3:
		if steps[2] not in CROP_MENU:
			return "CON Invalid crop. Select:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice"
		return "CON Enter acreage (e.g. 2.5):"

	if len(steps) == 4:
		try:
			acreage = Decimal(steps[3])
			if acreage <= 0:
				raise InvalidOperation
		except (InvalidOperation, ValueError):
			return "CON Invalid acreage. Enter a number (e.g. 2.5):"
		return f"CON Confirm M-Pesa number:\n1. Use {phone}\n2. Enter different number"

	if len(steps) == 5:
		mpesa = phone if steps[4] == "1" else normalize_phone(steps[4])
		return _finalize_registration(phone, steps[1], steps[2], Decimal(steps[3]), mpesa)

	return "END Session expired. Dial again to restart."
