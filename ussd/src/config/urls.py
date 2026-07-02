"""Root URL configuration for the USSD service."""

from __future__ import annotations

from django.http import JsonResponse
from django.urls import include, path
from django.utils import timezone

from src.config import settings


def health_check(_request):
	return JsonResponse(
		{
			"status": "healthy",
			"service": "bimagrid-ussd",
			"version": settings.USSD_VERSION,
			"timestamp": timezone.now().isoformat(),
		}
	)


urlpatterns = [
	path("health/", health_check, name="health-check"),
	path("ussd/", include("src.gateway.urls")),
]
