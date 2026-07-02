"""USSD gateway URL routing."""

from __future__ import annotations

from django.urls import path

from src.gateway.views import UssdGatewayView

urlpatterns = [
	path("gateway/", UssdGatewayView.as_view(), name="ussd-gateway"),
]
