"""Shared project constants."""

from __future__ import annotations

DEFAULT_CURRENCY = "KES"
DEFAULT_TIMEZONE = "Africa/Nairobi"

POLICY_STATUS_ACTIVE = "active"
POLICY_STATUS_PAID_OUT = "paid_out"

ORACLE_CONSENSUS_THRESHOLD = 3
DROUGHT_RAINFALL_THRESHOLD_MM = 30.0

MITIGATION_TYPES = (
	"drip_irrigation",
	"mulching",
	"terracing",
	"cover_crop",
)
