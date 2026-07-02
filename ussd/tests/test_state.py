"""Session storage tests."""

from src.state.models import UssdSession
from src.state.storage import InMemorySessionStorage


def test_in_memory_session_roundtrip():
	storage = InMemorySessionStorage(ttl_seconds=60)
	session = UssdSession(session_id="abc", phone_number="254712345678", flow="registration")
	storage.save(session)
	loaded = storage.get("abc")
	assert loaded is not None
	assert loaded.flow == "registration"
	storage.delete("abc")
	assert storage.get("abc") is None
