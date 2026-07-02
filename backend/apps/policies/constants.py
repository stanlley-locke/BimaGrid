"""Policy domain constants."""

from __future__ import annotations

POLICY_TRANSITIONS: dict[str, set[str]] = {
	"draft": {"active", "cancelled"},
	"active": {"lapsed", "cancelled", "paid_out"},
	"lapsed": set(),
	"cancelled": set(),
	"paid_out": set(),
}

DEFAULT_COVERAGE_DAYS = 180
DROUGHT_TRIGGER_RAINFALL_MM = 30.0
