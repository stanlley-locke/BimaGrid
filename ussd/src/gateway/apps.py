"""USSD gateway Django application."""

from django.apps import AppConfig


class GatewayConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "src.gateway"
	verbose_name = "USSD Gateway"
