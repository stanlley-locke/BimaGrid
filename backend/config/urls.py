"""Root URL configuration for the BimaGrid backend."""

from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.utils import timezone


def health_check(_request):
	return JsonResponse(
		{
			"status": "healthy",
			"version": settings.BIMAGRID_VERSION,
			"timestamp": timezone.now().isoformat(),
		}
	)


def _api_v1_patterns():
	return [
		path("accounts/", include("apps.accounts.urls")),
		path("onboarding/", include("apps.onboarding.urls")),
		path("", include("apps.policies.urls")),
		path("", include("apps.pricing.urls")),
		path("", include("apps.claims.urls")),
		path("", include("apps.geospatial.urls")),
		path("", include("apps.notifications.urls")),
		path("", include("apps.payments.urls")),
		path("", include("apps.oracles.urls")),
		path("", include("apps.verification.urls")),
		path("", include("apps.satellite.urls")),
		path("admin/", include("apps.admin_dashboard.urls")),
		path("ussd/", include("apps.ussd.urls")),
	]


urlpatterns = [
	path("admin/", admin.site.urls),
	path("health/", health_check, name="health-check"),
	path("api/health/", health_check, name="api-health-check"),
	path("ussd/", include("apps.ussd.urls")),
	path("api/v1/", include(_api_v1_patterns())),
	# Backward-compatible /api/ routes (same handlers as v1)
	path("api/accounts/", include("apps.accounts.urls")),
	path("api/onboarding/", include("apps.onboarding.urls")),
	path("api/", include("apps.policies.urls")),
	path("api/", include("apps.pricing.urls")),
	path("api/", include("apps.claims.urls")),
	path("api/", include("apps.geospatial.urls")),
	path("api/", include("apps.notifications.urls")),
	path("api/", include("apps.payments.urls")),
	path("api/", include("apps.oracles.urls")),
	path("api/", include("apps.verification.urls")),
	path("api/", include("apps.satellite.urls")),
	path("api/admin/", include("apps.admin_dashboard.urls")),
]
