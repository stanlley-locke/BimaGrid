"""Internal USSD API endpoints for the standalone USSD service."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Profile
from apps.claims.models import Claim
from apps.onboarding.constants import CropChoice
from apps.onboarding.services import get_or_create_onboarding, submit_onboarding
from apps.policies.models import Policy

from .services import get_or_create_farmer_profile, normalize_phone


def _authorize_internal_request(request) -> bool:
	expected = getattr(settings, "USSD_INTERNAL_API_KEY", "")
	if not expected:
		return settings.DEBUG
	received = request.headers.get("X-USSD-Internal-Key", "")
	return received == expected


class UssdInternalRegisterView(APIView):
	"""POST /api/v1/ussd/internal/register/ — create onboarding from USSD."""

	authentication_classes = []
	permission_classes = []

	def post(self, request):
		if not _authorize_internal_request(request):
			return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

		phone = normalize_phone(str(request.data.get("phone", "")))
		ward_code = str(request.data.get("ward_code", "")).strip()
		ward_id = str(request.data.get("ward_id", "")).strip()
		crop = str(request.data.get("crop", "")).strip()
		mpesa_number = normalize_phone(str(request.data.get("mpesa_number", phone)))

		try:
			acreage = Decimal(str(request.data.get("acreage", "0")))
			if acreage <= 0:
				raise InvalidOperation
		except (InvalidOperation, ValueError):
			return Response({"error": "Invalid acreage"}, status=status.HTTP_400_BAD_REQUEST)

		from apps.geospatial.models import Ward

		ward = None
		if ward_id:
			ward = Ward.objects.filter(id=ward_id).first()
			if not ward:
				return Response({"error": "Invalid ward_id"}, status=status.HTTP_400_BAD_REQUEST)
			ward_code = ward.ward_code
		elif len(ward_code) != 4 or not ward_code.isdigit():
			return Response({"error": "Invalid ward code"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			ward = Ward.objects.filter(external_id=int(ward_code)).first()

		if crop not in CropChoice.values:
			return Response({"error": "Invalid crop"}, status=status.HTTP_400_BAD_REQUEST)

		profile = get_or_create_farmer_profile(phone)
		onboarding = get_or_create_onboarding(profile)
		onboarding.ward = ward
		onboarding.ward_code = ward_code
		onboarding.crop = crop
		onboarding.acreage = acreage
		onboarding.mpesa_number = mpesa_number
		onboarding.save(
			update_fields=["ward", "ward_code", "crop", "acreage", "mpesa_number", "updated_at"]
		)
		submit_onboarding(onboarding)
		if ward:
			from apps.geospatial.tasks import profile_ward_area

			profile_ward_area.delay(str(ward.id))

		return Response(
			{
				"status": "submitted",
				"phone": phone,
				"ward_code": ward_code,
				"crop": crop,
				"acreage": str(acreage),
				"mpesa_number": mpesa_number,
				"onboarding_status": onboarding.status,
				"message": "Premium quote pending agent review.",
			},
			status=status.HTTP_201_CREATED,
		)


class UssdInternalPolicyStatusView(APIView):
	"""GET /api/v1/ussd/internal/policy-status/?phone=254..."""

	authentication_classes = []
	permission_classes = []

	def get(self, request):
		if not _authorize_internal_request(request):
			return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

		phone = normalize_phone(str(request.query_params.get("phone", "")))
		if not phone:
			return Response({"error": "phone is required"}, status=status.HTTP_400_BAD_REQUEST)

		profile = Profile.objects.filter(phone_number=phone).first()
		if not profile:
			return Response(
				{
					"status": "not_found",
					"message": "No BimaGrid account found. Dial again and choose 1 to register.",
				}
			)

		onboarding = getattr(profile, "onboarding", None)
		if not onboarding:
			return Response(
				{
					"status": "incomplete",
					"message": "Registration incomplete. Choose 1 to register your farm.",
				}
			)

		policy = Policy.objects.filter(onboarding=onboarding).order_by("-created_at").first()
		if not policy:
			return Response(
				{
					"status": "no_policy",
					"message": f"Onboarding {onboarding.status}. No policy issued yet.",
					"onboarding_status": onboarding.status,
				}
			)

		return Response(
			{
				"status": "ok",
				"policy_number": policy.policy_number,
				"crop": policy.crop,
				"policy_status": policy.status,
				"premium_amount": str(policy.premium_amount),
			}
		)


class UssdInternalClaimView(APIView):
	"""POST /api/v1/ussd/internal/claim/ — parametric claim status / filing."""

	authentication_classes = []
	permission_classes = []

	def post(self, request):
		if not _authorize_internal_request(request):
			return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

		phone = normalize_phone(str(request.data.get("phone", "")))
		loss_type = str(request.data.get("loss_type", "drought")).strip()

		profile = Profile.objects.filter(phone_number=phone).first()
		if not profile:
			return Response(
				{
					"status": "not_found",
					"message": "No BimaGrid account found. Register first (option 1).",
				}
			)

		onboarding = getattr(profile, "onboarding", None)
		if not onboarding:
			return Response(
				{
					"status": "incomplete",
					"message": "Complete farm registration before checking claims.",
				}
			)

		policy = Policy.objects.filter(onboarding=onboarding).order_by("-created_at").first()
		if not policy:
			return Response(
				{
					"status": "no_policy",
					"message": "No active policy. Parametric claims require an active policy.",
				}
			)

		existing = Claim.objects.filter(policy=policy).order_by("-created_at").first()
		if existing:
			return Response(
				{
					"status": "existing",
					"claim_number": existing.claim_number,
					"claim_status": existing.status,
					"message": (
						f"Claim {existing.claim_number} status: {existing.status.upper()}. "
						"Parametric payouts trigger automatically when oracle consensus confirms peril."
					),
				}
			)

		return Response(
			{
				"status": "automatic",
				"policy_number": policy.policy_number,
				"loss_type": loss_type,
				"message": (
					"Parametric claims are automatic. No manual filing needed when drought "
					f"is detected for policy {policy.policy_number}."
				),
			}
		)
