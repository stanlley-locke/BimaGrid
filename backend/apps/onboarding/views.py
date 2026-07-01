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
