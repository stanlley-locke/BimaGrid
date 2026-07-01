"""Onboarding validators."""

from django.core.exceptions import ValidationError


def validate_positive_acreage(value):
	if value <= 0:
		raise ValidationError("Acreage must be greater than zero.")


def validate_mpesa_number(value: str) -> None:
	cleaned = value.replace("+", "").replace(" ", "")
	if not cleaned.isdigit() or len(cleaned) < 9:
		raise ValidationError("Enter a valid M-Pesa number.")


def validate_geojson_geometry(value):
	if not isinstance(value, dict):
		raise ValidationError("Geometry must be a JSON object.")
	if value.get("type") not in {"Polygon", "MultiPolygon"}:
		raise ValidationError("Geometry must be a Polygon or MultiPolygon GeoJSON object.")
