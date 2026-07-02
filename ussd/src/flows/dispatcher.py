"""USSD flow dispatcher."""

from __future__ import annotations

from src.flows.claims import ClaimsFlow
from src.flows.policy_status import PolicyStatusFlow
from src.flows.registration import RegistrationFlow
from src.screens import invalid_option, session_expired, welcome_menu
from src.state.manager import get_session_manager
from src.state.models import UssdSession
from src.utils.constants import MAIN_MENU_OPTIONS
from src.utils.parsing import parse_ussd_text
from src.utils.phone import normalize_phone

FLOWS = {
	"registration": RegistrationFlow(),
	"policy_status": PolicyStatusFlow(),
	"claims": ClaimsFlow(),
}


def handle_ussd_session(session_id: str, phone_number: str, text: str) -> str:
	"""Route USSD input to the appropriate flow and return CON/END response."""
	steps = parse_ussd_text(text)
	phone = normalize_phone(phone_number)
	manager = get_session_manager()
	session = manager.get_or_create(session_id, phone)

	if not steps:
		manager.update(session_id, flow="main", step=0, data={})
		return welcome_menu()

	main_choice = steps[0]
	flow_key = MAIN_MENU_OPTIONS.get(main_choice)
	if not flow_key:
		manager.clear(session_id)
		return invalid_option()

	manager.update(session_id, flow=flow_key, step=len(steps))
	flow = FLOWS.get(flow_key)
	if not flow:
		return session_expired()

	return flow.handle(session, steps)


def dispatch_flow(session: UssdSession, steps: list[str]) -> str:
	"""Dispatch to a flow using session metadata."""
	flow = FLOWS.get(session.flow)
	if not flow:
		return welcome_menu()
	return flow.handle(session, steps)
