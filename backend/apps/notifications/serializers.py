"""Notification serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import Notification, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
	class Meta:
		model = NotificationTemplate
		fields = ["id", "code", "subject", "body", "channel", "active", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class NotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Notification
		fields = ["id", "user", "template", "channel", "subject", "body", "status", "delivered_at", "metadata", "created_at", "updated_at"]
		read_only_fields = ["id", "status", "delivered_at", "created_at", "updated_at"]
