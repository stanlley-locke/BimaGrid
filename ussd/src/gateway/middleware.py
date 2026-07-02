"""USSD gateway middleware."""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
	def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
		self.get_response = get_response

	def __call__(self, request: HttpRequest) -> HttpResponse:
		start = time.perf_counter()
		response = self.get_response(request)
		duration_ms = (time.perf_counter() - start) * 1000
		logger.info(
			"%s %s status=%s duration_ms=%.2f",
			request.method,
			request.path,
			response.status_code,
			duration_ms,
		)
		return response


class RateLimitMiddleware:
	"""Sliding-window rate limiter keyed by client IP."""

	def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
		self.get_response = get_response
		self._limit = settings.RATE_LIMIT_REQUESTS
		self._window = settings.RATE_LIMIT_WINDOW_SECONDS
		self._hits: dict[str, deque[float]] = defaultdict(deque)

	def _client_ip(self, request: HttpRequest) -> str:
		forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
		if forwarded:
			return forwarded.split(",")[0].strip()
		return request.META.get("REMOTE_ADDR", "unknown")

	def _is_limited(self, ip: str) -> bool:
		now = time.time()
		window_start = now - self._window
		hits = self._hits[ip]
		while hits and hits[0] < window_start:
			hits.popleft()
		if len(hits) >= self._limit:
			return True
		hits.append(now)
		return False

	def __call__(self, request: HttpRequest) -> HttpResponse:
		if request.path.startswith("/ussd/"):
			ip = self._client_ip(request)
			if self._is_limited(ip):
				logger.warning("Rate limit exceeded for IP %s", ip)
				return JsonResponse(
					{"error": "Rate limit exceeded", "retry_after": self._window},
					status=429,
				)
		return self.get_response(request)
