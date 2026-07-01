"""Notification admin."""

from django.contrib import admin

from .models import Notification, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
	list_display = ("code", "channel", "active")
	search_fields = ("code", "subject")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "channel", "subject", "status", "delivered_at")
	raw_id_fields = ("user", "template")
