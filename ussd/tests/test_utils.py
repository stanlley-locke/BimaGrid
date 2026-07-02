"""Utility unit tests."""

from src.utils.phone import is_valid_kenyan_phone, normalize_phone
from src.utils.parsing import parse_ussd_text


def test_normalize_phone_from_local():
	assert normalize_phone("0712345678") == "254712345678"


def test_normalize_phone_from_international():
	assert normalize_phone("254712345678") == "254712345678"


def test_is_valid_kenyan_phone():
	assert is_valid_kenyan_phone("254712345678") is True
	assert is_valid_kenyan_phone("1234") is False


def test_parse_ussd_text():
	assert parse_ussd_text("") == []
	assert parse_ussd_text("1*1234*2") == ["1", "1234", "2"]
