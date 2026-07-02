"""Base USSD flow class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.state.models import UssdSession


class BaseFlow(ABC):
	"""Base class for multi-step USSD flows."""

	name: str = "base"

	@abstractmethod
	def handle(self, session: UssdSession, steps: list[str]) -> str:
		raise NotImplementedError

	def continue_response(self, message: str) -> str:
		return f"CON {message.strip()}"

	def end_response(self, message: str) -> str:
		return f"END {message.strip()}"

	def step_count(self, steps: list[str]) -> int:
		return len(steps)
