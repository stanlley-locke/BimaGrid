"""Shared core utilities."""

from __future__ import annotations

import uuid


def build_reference_code(prefix: str, identifier: uuid.UUID | None = None) -> str:
	value = identifier or uuid.uuid4()
	return f"{prefix.upper()}-{str(value).split('-')[0].upper()}"
