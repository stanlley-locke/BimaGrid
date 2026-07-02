"""Session state models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UssdSession:
	session_id: str
	phone_number: str
	flow: str = "main"
	data: dict[str, Any] = field(default_factory=dict)
	step: int = 0

	def to_dict(self) -> dict[str, Any]:
		return asdict(self)

	@classmethod
	def from_dict(cls, payload: dict[str, Any]) -> "UssdSession":
		return cls(
			session_id=payload["session_id"],
			phone_number=payload["phone_number"],
			flow=payload.get("flow", "main"),
			data=payload.get("data", {}),
			step=payload.get("step", 0),
		)
