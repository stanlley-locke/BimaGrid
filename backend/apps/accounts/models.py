"""Accounts domain models."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class TimeStampedUUIDModel(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Profile(TimeStampedUUIDModel):
	class Role(models.TextChoices):
		CUSTOMER = "customer", "Customer"
		FARMER = "farmer", "Farmer"
		BROKER = "broker", "Broker"
		COOP = "coop", "Co-op"
		ADMIN = "admin", "Admin"

	class Language(models.TextChoices):
		ENGLISH = "en", "English"
		SWAHILI = "sw", "Swahili"

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	full_name = models.CharField(max_length=255, blank=True)
	phone_number = models.CharField(max_length=32, blank=True)
	national_id = models.CharField(max_length=64, blank=True)
	role = models.CharField(max_length=16, choices=Role.choices, default=Role.CUSTOMER)
	preferred_language = models.CharField(max_length=8, choices=Language.choices, default=Language.ENGLISH)
	is_phone_verified = models.BooleanField(default=False)
	requires_password_change = models.BooleanField(default=False)

	class Meta:
		ordering = ["full_name", "user__username"]
		indexes = [
			models.Index(fields=["phone_number"]),
			models.Index(fields=["national_id"]),
		]

	def __str__(self) -> str:
		return self.full_name or self.user.get_username()
