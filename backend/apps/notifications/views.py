"""Notification API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Notification, NotificationTemplate
from .serializers import NotificationSerializer, NotificationTemplateSerializer


class NotificationTemplateViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = NotificationTemplateSerializer
	queryset = NotificationTemplate.objects.all()


class NotificationViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = NotificationSerializer

	def get_queryset(self):
		return Notification.objects.select_related("user", "template").all()
