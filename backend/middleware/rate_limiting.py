"""Simple in-memory rate limiting for API endpoints."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from django.conf import settings
from django.http import JsonResponse


class SimpleRateLimitMiddleware:
	"""Per-IP sliding-window rate limiter for /api/ routes."""

	_store: dict[str, deque[float]] = defaultdict(deque)
	_lock = Lock()

	def __init__(self, get_response):
		self.get_response = get_response
		self.max_requests = getattr(settings, "RATE_LIMIT_REQUESTS", 120)
		self.window_seconds = getattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 60)

	def __call__(self, request):
		if not request.path.startswith("/api/"):
			return self.get_response(request)

		client_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
		if not client_ip:
			client_ip = request.META.get("REMOTE_ADDR", "unknown")
		key = f"{client_ip}:{request.path.split('/')[1:3]}"

		now = time.monotonic()
		with self._lock:
			window = self._store[key]
			while window and now - window[0] > self.window_seconds:
				window.popleft()
			if len(window) >= self.max_requests:
				retry_after = max(1, int(self.window_seconds - (now - window[0])))
				return JsonResponse(
					{"error": "Rate limit exceeded", "retry_after_seconds": retry_after},
					status=429,
					headers={"Retry-After": str(retry_after)},
				)
			window.append(now)

		return self.get_response(request)
