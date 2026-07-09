"""Accounts views."""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from rest_framework.authtoken.models import Token

from .serializers import (
	AccountSerializer,
	LoginSerializer,
	RegistrationResponseSerializer,
	RegistrationSerializer,
)
from .services import get_or_create_profile


class LoginView(GenericAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = LoginSerializer

	def post(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data["user"]
		profile = get_or_create_profile(user)
		token, _ = Token.objects.get_or_create(user=user)
		return Response(
			{
				"token": token.key,
				"user": AccountSerializer(user).data,
				"requires_password_change": profile.requires_password_change,
			},
			status=status.HTTP_200_OK,
		)


class RegistrationView(GenericAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = RegistrationSerializer

	def post(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		response = RegistrationResponseSerializer(user)
		return Response(response.data, status=status.HTTP_201_CREATED)


class CurrentAccountView(RetrieveUpdateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = AccountSerializer

	def get_object(self):
		get_or_create_profile(self.request.user)
		return self.request.user

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop("partial", False)
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer)
		return Response(serializer.data)


class ForcePasswordResetView(GenericAPIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		new_password = request.data.get("new_password")
		if not new_password:
			return Response({"detail": "new_password is required."}, status=status.HTTP_400_BAD_REQUEST)
		
		user = request.user
		profile = get_or_create_profile(user)
		
		if not profile.requires_password_change:
			return Response({"detail": "Password reset not required."}, status=status.HTTP_400_BAD_REQUEST)
			
		user.set_password(new_password)
		user.save()
		
		profile.requires_password_change = False
		profile.save(update_fields=["requires_password_change"])
		
		return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
