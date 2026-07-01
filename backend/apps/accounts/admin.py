"""Accounts admin."""

from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "full_name", "phone_number", "national_id", "role", "preferred_language", "is_phone_verified")
	search_fields = ("user__username", "user__email", "full_name", "phone_number", "national_id")
	list_filter = ("role", "preferred_language", "is_phone_verified")
	raw_id_fields = ("user",)
