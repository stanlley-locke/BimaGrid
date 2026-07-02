"""USSD input parsing utilities."""

from __future__ import annotations


def parse_ussd_text(text: str) -> list[str]:
	"""Split Africa's Talking cumulative USSD input into steps."""
	if not text:
		return []
	return [step.strip() for step in text.split("*")]


def current_step_index(steps: list[str]) -> int:
	"""Return zero-based index of the latest user input step."""
	return max(len(steps) - 1, 0)


def last_input(steps: list[str]) -> str:
	if not steps:
		return ""
	return steps[-1]
