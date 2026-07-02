"""USSD URL routing."""

from django.urls import path

from .internal_views import (
	UssdInternalClaimView,
	UssdInternalPolicyStatusView,
	UssdInternalRegisterView,
)
from .views import UssdGatewayView


urlpatterns = [
	path("gateway/", UssdGatewayView.as_view(), name="ussd-gateway"),
	path("internal/register/", UssdInternalRegisterView.as_view(), name="ussd-internal-register"),
	path(
		"internal/policy-status/",
		UssdInternalPolicyStatusView.as_view(),
		name="ussd-internal-policy-status",
	),
	path("internal/claim/", UssdInternalClaimView.as_view(), name="ussd-internal-claim"),
]
