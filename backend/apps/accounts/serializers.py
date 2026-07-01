"""Accounts serializers."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Profile
from .services import sync_profile_fields


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = Profile
		fields = [
			"id",
			"full_name",
			"phone_number",
			"national_id",
			"role",
			"preferred_language",
			"is_phone_verified",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "is_phone_verified", "created_at", "updated_at"]


class AccountSerializer(serializers.ModelSerializer):
	profile = ProfileSerializer(required=False)

	class Meta:
		model = User
		fields = ["id", "username", "email", "first_name", "last_name", "profile"]
		read_only_fields = ["id"]

	def update(self, instance, validated_data):
		profile_data = validated_data.pop("profile", None)
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		if validated_data:
			instance.save(update_fields=[*validated_data.keys()])
		else:
			instance.save()
		if profile_data is not None:
			sync_profile_fields(instance, profile_data)
		return instance


class RegistrationSerializer(serializers.Serializer):
	username = serializers.CharField(max_length=150)
	email = serializers.EmailField()
	password = serializers.CharField(write_only=True, min_length=8)
	first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
	last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
	full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
	phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
	national_id = serializers.CharField(max_length=64, required=False, allow_blank=True)
	role = serializers.ChoiceField(choices=Profile.Role.choices, required=False)
	preferred_language = serializers.ChoiceField(choices=Profile.Language.choices, required=False)

	def validate_username(self, value: str) -> str:
		if User.objects.filter(username__iexact=value).exists():
			raise serializers.ValidationError("A user with this username already exists.")
		return value

	def validate_email(self, value: str) -> str:
		if User.objects.filter(email__iexact=value).exists():
			raise serializers.ValidationError("A user with this email already exists.")
		return value

	@transaction.atomic
	def create(self, validated_data):
		profile_data = {
			"full_name": validated_data.pop("full_name", ""),
			"phone_number": validated_data.pop("phone_number", ""),
			"national_id": validated_data.pop("national_id", ""),
			"role": validated_data.pop("role", Profile.Role.CUSTOMER),
			"preferred_language": validated_data.pop("preferred_language", Profile.Language.ENGLISH),
		}
		password = validated_data.pop("password")
		user = User.objects.create_user(password=password, **validated_data)
		Profile.objects.create(user=user, **profile_data)
		return user


class RegistrationResponseSerializer(serializers.ModelSerializer):
	profile = ProfileSerializer(read_only=True)

	class Meta:
		model = User
		fields = ["id", "username", "email", "first_name", "last_name", "profile"]
