"""Shared test fixtures."""

from __future__ import annotations

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
django.setup()

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile

User = get_user_model()


@pytest.fixture
def api_client():
	from rest_framework.test import APIClient

	return APIClient()


@pytest.fixture
def admin_user(db):
	user = User.objects.create_user(
		username="admin_user",
		email="admin@example.com",
		password="test-pass-123",
		is_staff=True,
	)
	profile = Profile.objects.create(user=user, full_name="Admin User", role=Profile.Role.ADMIN)
	return user, profile


@pytest.fixture
def broker_user(db):
	user = User.objects.create_user(
		username="broker_user",
		email="broker@example.com",
		password="test-pass-123",
	)
	profile = Profile.objects.create(user=user, full_name="Broker User", role=Profile.Role.BROKER)
	return user, profile


@pytest.fixture
def farmer_user(db):
	user = User.objects.create_user(
		username="farmer_user",
		email="farmer@example.com",
		password="test-pass-123",
	)
	profile = Profile.objects.create(
		user=user,
		full_name="Farmer User",
		phone_number="254712345678",
		role=Profile.Role.FARMER,
	)
	onboarding = profile.onboarding
	return user, profile, onboarding
