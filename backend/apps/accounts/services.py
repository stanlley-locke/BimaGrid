"""Accounts domain services."""

from __future__ import annotations

from django.contrib.auth import get_user_model

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