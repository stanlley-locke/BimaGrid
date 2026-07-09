"""Onboarding views."""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FarmerOnboardingSerializer
from .services import get_or_create_onboarding, submit_onboarding


class CurrentOnboardingView(RetrieveUpdateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = FarmerOnboardingSerializer

	def get_object(self):
		return get_or_create_onboarding(self.request.user.profile)

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context["profile"] = self.request.user.profile
		return context


class SubmitOnboardingView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		onboarding = get_or_create_onboarding(request.user.profile)
		serializer = FarmerOnboardingSerializer(onboarding, data=request.data, partial=True, context={"profile": request.user.profile, "request": request})
		serializer.is_valid(raise_exception=True)
		onboarding = serializer.save()
		onboarding = submit_onboarding(onboarding)
		return Response(FarmerOnboardingSerializer(onboarding).data, status=status.HTTP_200_OK)

class OnboardingStatusView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, *args, **kwargs):
		onboarding = get_or_create_onboarding(request.user.profile)
		return Response({"status": onboarding.status, "verification_level": onboarding.verification_level})

class VerifyIdentityView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		onboarding = get_or_create_onboarding(request.user.profile)
		onboarding.verification_level = 2
		onboarding.save(update_fields=["verification_level", "updated_at"])
		return Response({"status": "verified", "verification_level": onboarding.verification_level})


from django.contrib.auth import get_user_model
from apps.accounts.models import Profile
from services.notification_service import notify_user
import secrets
import string

User = get_user_model()

class AgentFarmerRegistrationView(APIView):
	"""Endpoint for agents to register a new farmer."""
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		# Validate data
		data = request.data
		phone = data.get("phone_number")
		email = data.get("email")
		full_name = data.get("full_name")

		if not phone or not full_name:
			return Response({"detail": "Phone number and full name are required."}, status=status.HTTP_400_BAD_REQUEST)

		if User.objects.filter(username=phone).exists():
			return Response({"detail": "Farmer with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

		# Generate temporary password
		alphabet = string.ascii_letters + string.digits
		temp_password = "".join(secrets.choice(alphabet) for i in range(8))

		# Create user
		user = User.objects.create_user(
			username=phone,
			password=temp_password,
			email=email or "",
		)

		# Create profile and flag for password change
		profile = Profile.objects.create(
			user=user,
			full_name=full_name,
			phone_number=phone,
			role=Profile.Role.FARMER,
			requires_password_change=True,
		)

		# Dispatch Welcome Notifications
		sms_body = f"Welcome to BimaGrid, {full_name}! Your temporary password is: {temp_password}. Dial *384*1234# to access the USSD portal."
		notify_user(user, "Welcome to BimaGrid", sms_body, channel="sms", metadata={"phone": phone})
		
		if email:
			email_body = f"<h2>Welcome to BimaGrid</h2><p>Hello {full_name},</p><p>Your account has been created. Your temporary password is: <b>{temp_password}</b></p><p>Please log in to the web portal or dial *384*1234# to set a new password.</p>"
			notify_user(user, "Welcome to BimaGrid", email_body, channel="email", metadata={"email": email})

		return Response({"detail": "Farmer registered successfully.", "temp_password": temp_password}, status=status.HTTP_201_CREATED)

