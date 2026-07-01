"""Payments admin."""

from django.contrib import admin

from .models import PaymentTransaction, Payout


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
	list_display = ("reference", "provider", "amount", "currency", "status", "processed_at")
	raw_id_fields = ("policy", "claim")


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
	list_display = ("reference", "policy", "amount", "phone_number", "status")
	raw_id_fields = ("policy",)
