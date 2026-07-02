"""USSD session state manager."""

from __future__ import annotations

from typing import Any

from src.state.models import UssdSession
from src.state.storage import SessionStorage, build_session_storage


class SessionManager:
	def __init__(self, storage: SessionStorage | None = None) -> None:
		self._storage = storage or build_session_storage()

	def get_or_create(self, session_id: str, phone_number: str) -> UssdSession:
		session = self._storage.get(session_id)
		if session:
			if session.phone_number != phone_number:
				session.phone_number = phone_number
				self._storage.save(session)
			return session
		session = UssdSession(session_id=session_id, phone_number=phone_number)
		self._storage.save(session)
		return session

	def update(
		self,
		session_id: str,
		*,
		flow: str | None = None,
		step: int | None = None,
		data: dict[str, Any] | None = None,
	) -> UssdSession | None:
		session = self._storage.get(session_id)
		if not session:
			return None
		if flow is not None:
			session.flow = flow
		if step is not None:
			session.step = step
		if data is not None:
			session.data.update(data)
		self._storage.save(session)
		return session

	def clear(self, session_id: str) -> None:
		self._storage.delete(session_id)


_default_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
	global _default_manager
	if _default_manager is None:
		_default_manager = SessionManager()
	return _default_manager
