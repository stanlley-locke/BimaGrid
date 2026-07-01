"""Root URL configuration for the BimaGrid backend."""

from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
	return JsonResponse({"status": "healthy", "service": "backend"})


urlpatterns = [
	path("admin/", admin.site.urls),
	path("health/", health_check, name="health-check"),
	path("api/accounts/", include("apps.accounts.urls")),
	path("api/onboarding/", include("apps.onboarding.urls")),
	path("api/", include("apps.policies.urls")),
	path("api/", include("apps.geospatial.urls")),
	path("api/", include("apps.notifications.urls")),
	path("api/", include("apps.payments.urls")),
	path("api/", include("apps.oracles.urls")),
	path("api/", include("apps.verification.urls")),
	path("api/", include("apps.satellite.urls")),
]
