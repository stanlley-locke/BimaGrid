"""Registration flow unit tests."""

from src.flows.registration.handlers import RegistrationFlow
from src.flows.registration.validators import (
	validate_acreage,
	validate_crop_choice,
	validate_ward_code,
)
from src.state.models import UssdSession


def test_validate_ward_code():
	assert validate_ward_code("1234") == (True, "1234")
	assert validate_ward_code("12") == (False, "12")


def test_validate_crop_choice():
	valid, code, label = validate_crop_choice("1")
	assert valid is True
	assert code == "maize"
	assert label == "Maize"


def test_validate_acreage():
	valid, value = validate_acreage("2.5")
	assert valid is True
	assert str(value) == "2.5"
	assert validate_acreage("-1")[0] is False


def test_registration_ward_prompt():
	flow = RegistrationFlow()
	session = UssdSession(session_id="s1", phone_number="254712345678")
	response = flow.handle(session, ["1"])
	assert response.startswith("CON Enter your 4-digit Ward Code")


def test_registration_invalid_ward():
	flow = RegistrationFlow()
	session = UssdSession(session_id="s1", phone_number="254712345678")
	response = flow.handle(session, ["1", "12"])
	assert "Invalid ward code" in response
