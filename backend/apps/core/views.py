from __future__ import annotations

from django.http import JsonResponse


def health_check(_request):
    return JsonResponse({"status": "healthy", "service": "core"})