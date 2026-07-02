"""USSD gateway tests."""

from unittest.mock import patch

from django.test import Client, TestCase, override_settings


class UssdGatewayTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_welcome_menu(self):
		response = self.client.post(
			"/ussd/gateway/",
			{"sessionId": "ATUid_test", "phoneNumber": "254712345678", "text": ""},
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.content.decode().startswith("CON Welcome to BimaGrid"))

	@override_settings(USSD_SERVICE_URL="http://ussd-service:8001")
	@patch("apps.ussd.services.requests.post")
	def test_proxy_to_standalone_when_configured(self, mock_post):
		mock_post.return_value.status_code = 200
		mock_post.return_value.text = "CON Proxied menu"
		mock_post.return_value.raise_for_status = lambda: None

		response = self.client.post(
			"/ussd/gateway/",
			{"sessionId": "ATUid_proxy", "phoneNumber": "254712345678", "text": ""},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), "CON Proxied menu")
		mock_post.assert_called_once()

	def test_registration_flow_completes(self):
		steps = [
			"1",
			"1*1234",
			"1*1234*1",
			"1*1234*1*2.5",
			"1*1234*1*2.5*1",
		]
		for text in steps:
			response = self.client.post(
				"/ussd/gateway/",
				{"sessionId": "ATUid_reg", "phoneNumber": "254712345678", "text": text},
			)
			self.assertEqual(response.status_code, 200)
		self.assertTrue(response.content.decode().startswith("END Registration complete"))

	def test_v1_ussd_route(self):
		response = self.client.post(
			"/api/v1/ussd/gateway/",
			{"sessionId": "ATUid_v1", "phoneNumber": "254712345678", "text": ""},
		)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b"BimaGrid", response.content)

	def test_health_includes_version(self):
		response = self.client.get("/health/")
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(data["status"], "healthy")
		self.assertIn("version", data)
