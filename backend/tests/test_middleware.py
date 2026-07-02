"""Middleware integration tests."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from apps.accounts.models import Profile

User = get_user_model()


class RequestIDMiddlewareTests(TestCase):
	def test_request_id_header_is_returned(self):
		client = Client()
		response = client.get("/health/")
		self.assertEqual(response.status_code, 200)
		self.assertIn("X-Request-ID", response)
		self.assertTrue(response["X-Request-ID"])

	def test_custom_request_id_is_echoed(self):
		client = Client()
		response = client.get("/health/", HTTP_X_REQUEST_ID="test-req-123")
		self.assertEqual(response["X-Request-ID"], "test-req-123")


class RequestTimingMiddlewareTests(TestCase):
	def test_response_time_header_is_set(self):
		client = Client()
		response = client.get("/health/")
		self.assertIn("X-Response-Time", response)
		self.assertTrue(response["X-Response-Time"].endswith("ms"))


@override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_WINDOW_SECONDS=60)
class RateLimitMiddlewareTests(TestCase):
	def setUp(self):
		self.client = Client()
		from middleware.rate_limiting import SimpleRateLimitMiddleware

		SimpleRateLimitMiddleware._store.clear()

	def test_rate_limit_applies_to_api_routes(self):
		for _ in range(2):
			response = self.client.get("/api/health/")
			self.assertEqual(response.status_code, 200)

		response = self.client.get("/api/health/")
		self.assertEqual(response.status_code, 429)
		self.assertIn("retry_after_seconds", response.json())

	def test_health_route_outside_api_is_not_limited(self):
		for _ in range(5):
			response = self.client.get("/health/")
			self.assertEqual(response.status_code, 200)


@override_settings(USSD_INTERNAL_API_KEY="secret-key")
class InternalApiKeyMiddlewareTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_internal_route_requires_key_when_configured(self):
		response = self.client.post(
			"/api/v1/ussd/internal/register/",
			{"phone": "254712345678", "ward_code": "1234", "crop": "maize", "acreage": "2.5"},
			content_type="application/json",
		)
		self.assertEqual(response.status_code, 401)

	def test_internal_route_accepts_valid_key(self):
		response = self.client.post(
			"/api/v1/ussd/internal/register/",
			{"phone": "254712345678", "ward_code": "1234", "crop": "maize", "acreage": "2.5"},
			content_type="application/json",
			HTTP_X_USSD_INTERNAL_KEY="secret-key",
		)
		self.assertEqual(response.status_code, 201)
