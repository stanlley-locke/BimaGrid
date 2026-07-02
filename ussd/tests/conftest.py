"""Pytest configuration for USSD service tests."""

import pytest

from src.state.storage import InMemorySessionStorage
from src.state.manager import SessionManager


@pytest.fixture(autouse=True)
def in_memory_sessions(monkeypatch):
	storage = InMemorySessionStorage(ttl_seconds=180)
	manager = SessionManager(storage=storage)
	monkeypatch.setattr("src.flows.dispatcher.get_session_manager", lambda: manager)
	monkeypatch.setattr("src.state.manager._default_manager", manager)
	yield manager
	manager._storage._store.clear()


@pytest.fixture
def mock_backend(mocker):
	client = mocker.Mock()
	client.register_farmer.return_value = {
		"status": "submitted",
		"message": "Premium quote pending agent review.",
	}
	client.get_policy_status.return_value = {
		"status": "ok",
		"policy_number": "POL-12345",
		"crop": "maize",
		"policy_status": "active",
		"premium_amount": "450.00",
	}
	client.file_claim.return_value = {
		"status": "automatic",
		"message": "Parametric claims are automatic when drought is detected.",
	}
	mocker.patch("src.flows.registration.handlers.get_backend_client", return_value=client)
	mocker.patch("src.flows.policy_status.get_backend_client", return_value=client)
	mocker.patch("src.flows.claims.get_backend_client", return_value=client)
	return client
