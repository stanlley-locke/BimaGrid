"""Session persistence backends."""

from __future__ import annotations

import json
import threading
import time
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings

from src.state.models import UssdSession


class SessionStorage(ABC):
	@abstractmethod
	def get(self, session_id: str) -> UssdSession | None:
		raise NotImplementedError

	@abstractmethod
	def save(self, session: UssdSession) -> None:
		raise NotImplementedError

	@abstractmethod
	def delete(self, session_id: str) -> None:
		raise NotImplementedError


class InMemorySessionStorage(SessionStorage):
	def __init__(self, ttl_seconds: int) -> None:
		self._ttl = ttl_seconds
		self._store: dict[str, tuple[float, dict[str, Any]]] = {}
		self._lock = threading.Lock()

	def _purge_expired(self) -> None:
		now = time.time()
		expired = [key for key, (expires_at, _) in self._store.items() if expires_at <= now]
		for key in expired:
			self._store.pop(key, None)

	def get(self, session_id: str) -> UssdSession | None:
		with self._lock:
			self._purge_expired()
			entry = self._store.get(session_id)
			if not entry:
				return None
			_, payload = entry
			return UssdSession.from_dict(payload)

	def save(self, session: UssdSession) -> None:
		with self._lock:
			self._store[session.session_id] = (
				time.time() + self._ttl,
				session.to_dict(),
			)

	def delete(self, session_id: str) -> None:
		with self._lock:
			self._store.pop(session_id, None)


class RedisSessionStorage(SessionStorage):
	def __init__(self, redis_url: str, ttl_seconds: int) -> None:
		import redis

		self._client = redis.from_url(redis_url, decode_responses=True)
		self._ttl = ttl_seconds
		self._prefix = "ussd:session:"

	def get(self, session_id: str) -> UssdSession | None:
		raw = self._client.get(f"{self._prefix}{session_id}")
		if not raw:
			return None
		return UssdSession.from_dict(json.loads(raw))

	def save(self, session: UssdSession) -> None:
		key = f"{self._prefix}{session.session_id}"
		self._client.setex(key, self._ttl, json.dumps(session.to_dict()))

	def delete(self, session_id: str) -> None:
		self._client.delete(f"{self._prefix}{session_id}")


def build_session_storage() -> SessionStorage:
	if settings.USE_IN_MEMORY_SESSIONS or not settings.REDIS_URL:
		return InMemorySessionStorage(settings.SESSION_TTL)
	return RedisSessionStorage(settings.REDIS_URL, settings.SESSION_TTL)
