"""Notification API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.permissions import IsAdminUser
from apps.core.queryset import is_admin, scope_user_queryset

from .models import Notification, NotificationTemplate
from .serializers import NotificationSerializer, NotificationTemplateSerializer


class NotificationTemplateViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated, IsAdminUser]
	serializer_class = NotificationTemplateSerializer
	queryset = NotificationTemplate.objects.all()
	filter_backends = [DjangoFilterBackend, SearchFilter]
	filterset_fields = ["channel", "active"]
	search_fields = ["code", "subject"]


class NotificationViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = NotificationSerializer
	filter_backends = [DjangoFilterBackend, OrderingFilter]
	filterset_fields = ["status", "channel"]
	ordering_fields = ["created_at"]

	def get_queryset(self):
		qs = Notification.objects.select_related("user", "template")
		if is_admin(self.request.user):
			return qs
		return scope_user_queryset(qs, self.request.user)

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
