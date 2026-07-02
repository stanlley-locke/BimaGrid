"""USSD gateway endpoint tests."""

import pytest
from django.test import Client


@pytest.fixture
def client():
	return Client()


def test_welcome_menu(client):
	response = client.post(
		"/ussd/gateway/",
		{"sessionId": "ATUid_test", "phoneNumber": "254712345678", "text": ""},
	)
	assert response.status_code == 200
	body = response.content.decode()
	assert body.startswith("CON Welcome to BimaGrid")
	assert "1. Register Farm" in body


def test_registration_flow_completes(client, mock_backend):
	steps = [
		"1",
		"1*1234",
		"1*1234*1",
		"1*1234*1*2.5",
		"1*1234*1*2.5*1",
	]
	for text in steps:
		response = client.post(
			"/ussd/gateway/",
			{"sessionId": "ATUid_reg", "phoneNumber": "254712345678", "text": text},
		)
		assert response.status_code == 200
	body = response.content.decode()
	assert body.startswith("END Registration complete")
	mock_backend.register_farmer.assert_called_once()


def test_policy_status(client, mock_backend):
	response = client.post(
		"/ussd/gateway/",
		{"sessionId": "ATUid_status", "phoneNumber": "254712345678", "text": "2"},
	)
	assert response.status_code == 200
	body = response.content.decode()
	assert body.startswith("END Policy POL-12345")
	mock_backend.get_policy_status.assert_called_once()


def test_claims_flow(client, mock_backend):
	response = client.post(
		"/ussd/gateway/",
		{"sessionId": "ATUid_claim", "phoneNumber": "254712345678", "text": "3*1"},
	)
	assert response.status_code == 200
	body = response.content.decode()
	assert body.startswith("END")
	mock_backend.file_claim.assert_called_once()


def test_health_check(client):
	response = client.get("/health/")
	assert response.status_code == 200
	data = response.json()
	assert data["status"] == "healthy"
	assert data["service"] == "bimagrid-ussd"
