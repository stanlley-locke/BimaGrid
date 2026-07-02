"""Accounts domain services."""

from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model

from .models import Profile


User = get_user_model()


def get_or_create_profile(user: User) -> Profile:
	profile, _ = Profile.objects.get_or_create(user=user)
	return profile


def sync_profile_fields(user: User, profile_data: dict) -> Profile:
	profile = get_or_create_profile(user)
	for field, value in profile_data.items():
		setattr(profile, field, value)
	profile.save()
	return profile


def resolve_user_for_login(identifier: str) -> User | None:
	"""Resolve username, email, or profile phone number to a user account."""
	identifier = identifier.strip()
	if not identifier:
		return None

	user = User.objects.filter(username__iexact=identifier).first()
	if user:
		return user

	user = User.objects.filter(email__iexact=identifier).first()
	if user:
		return user

	profile = (
		Profile.objects.filter(phone_number=identifier)
		.select_related("user")
		.first()
	)
	if profile:
		return profile.user

	normalized = identifier.lstrip("+").replace(" ", "")
	if normalized.startswith("0") and len(normalized) == 10:
		normalized = f"254{normalized[1:]}"

	profile = (
		Profile.objects.filter(phone_number=normalized)
		.select_related("user")
		.first()
	)
	return profile.user if profile else None


def authenticate_with_identifier(identifier: str, password: str) -> User | None:
	user = resolve_user_for_login(identifier)
	if user is None:
		return None
	return authenticate(username=user.username, password=password)
