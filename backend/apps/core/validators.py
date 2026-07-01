"""Shared core validators."""

from django.core.exceptions import ValidationError


def validate_non_negative_decimal(value):
	if value < 0:
		raise ValidationError("Value must be zero or greater.")
