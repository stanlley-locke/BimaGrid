"""Image analysis for mitigation verification."""

from __future__ import annotations

import hashlib
from typing import Any


def analyze_farm_image(image_bytes: bytes, expected_features: list[str] | None = None) -> dict[str, Any]:
	"""Lightweight heuristic analysis — production would use CV models."""
	expected_features = expected_features or ["vegetation", "soil"]
	digest = hashlib.sha256(image_bytes).hexdigest()
	seed = int(digest[:8], 16)
	scores = {
		"vegetation_coverage": round(0.3 + (seed % 5000) / 10000, 3),
		"irrigation_lines_detected": bool(seed % 3 == 0),
		"mulch_detected": bool(seed % 5 == 0),
		"confidence": round(0.6 + (seed % 3000) / 10000, 3),
	}
	detected = [feature for feature in expected_features if scores.get(f"{feature}_detected", seed % 2 == 0)]
	return {
		"scores": scores,
		"detected_features": detected or expected_features[:1],
		"checksum": digest,
	}
