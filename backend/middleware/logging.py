"""Request logging and timing middleware."""

from __future__ import annotations

import logging
import time

logger = logging.getLogger("bimagrid.request")


class RequestTimingMiddleware:
	"""Attach request duration and emit structured access logs."""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		start = time.perf_counter()
		response = self.get_response(request)
		duration_ms = (time.perf_counter() - start) * 1000
		response["X-Response-Time"] = f"{duration_ms:.2f}ms"
		request_id = getattr(request, "request_id", "-")
		logger.info(
			"%s %s %s %.2fms",
			request.method,
			request.path,
			response.status_code,
			duration_ms,
			extra={
				"request_id": request_id,
				"method": request.method,
				"path": request.path,
				"status_code": response.status_code,
				"duration_ms": round(duration_ms, 2),
			},
		)
		return response
