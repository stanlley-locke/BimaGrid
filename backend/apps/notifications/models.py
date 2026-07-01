"""Notification domain models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedUUIDModel


class NotificationTemplate(TimeStampedUUIDModel):
	code = models.CharField(max_length=64, unique=True)
	subject = models.CharField(max_length=255)
	body = models.TextField()
	channel = models.CharField(max_length=32, default="email")
	active = models.BooleanField(default=True)


class Notification(TimeStampedUUIDModel):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		SENT = "sent", "Sent"
		FAILED = "failed", "Failed"

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
	template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications")
	channel = models.CharField(max_length=32, default="email")
	subject = models.CharField(max_length=255)
	body = models.TextField()
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	delivered_at = models.DateTimeField(null=True, blank=True)
	metadata = models.JSONField(default=dict, blank=True)
