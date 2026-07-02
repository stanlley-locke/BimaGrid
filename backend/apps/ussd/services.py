"""USSD session flow logic for Africa's Talking gateway."""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile
from apps.onboarding.constants import CropChoice
from apps.onboarding.models import FarmerOnboarding
from apps.onboarding.services import get_or_create_onboarding, submit_onboarding
from apps.policies.models import Policy

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

	if len(steps) == 1:
		return "CON Enter your 4-digit Ward Code:"

	if len(steps) == 2:
		ward = steps[1].strip()
		if len(ward) != 4 or not ward.isdigit():
			return "CON Invalid ward code. Enter 4 digits:"
		return "CON Select crop:\n1. Maize\n2. Beans\n3. Wheat\n4. Rice"

	if len(steps) == 3:
		crop = CROP_MENU.get(steps[2])
		if not crop:
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
		profile = get_or_create_farmer_profile(phone)
		onboarding = get_or_create_onboarding(profile)
		onboarding.ward_code = steps[1]
		onboarding.crop = CROP_MENU[steps[2]]
		onboarding.acreage = Decimal(steps[3])
		onboarding.mpesa_number = mpesa
		onboarding.save(
			update_fields=["ward_code", "crop", "acreage", "mpesa_number", "updated_at"]
		)
		submit_onboarding(onboarding)
		return (
			f"END Registration complete.\n"
			f"Ward: {onboarding.ward_code}\n"
			f"Crop: {onboarding.crop}\n"
			f"Acreage: {onboarding.acreage}\n"
			f"Premium quote pending agent review."
		)

	return "END Session expired. Dial again to restart."
