"""USSD hierarchical geography menu helpers."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.geospatial.models import Constituency, County, SubCounty, Ward

PAGE_SIZE = 7
NEXT_PAGE_TOKEN = "8"


def _paginated_menu(
	items: list[tuple[str, str]],
	page: int,
	title: str,
) -> str:
	start = page * PAGE_SIZE
	chunk = items[start : start + PAGE_SIZE]
	if not chunk and page > 0:
		chunk = items[0:PAGE_SIZE]
		page = 0
	lines = [title]
	for index, (_, label) in enumerate(chunk, start=1):
		lines.append(f"{index}. {label[:22]}")
	if start + PAGE_SIZE < len(items):
		lines.append(f"{NEXT_PAGE_TOKEN}. Next page")
	return "CON " + "\n".join(lines)


def _parse_page_selection(steps: list[str]) -> tuple[int, int]:
	if not steps:
		return 0, 0
	page = 0
	for step in steps[:-1]:
		if step == NEXT_PAGE_TOKEN:
			page += 1
	try:
		selection = int(steps[-1])
	except (TypeError, ValueError):
		return page, 0
	if steps[-1] == NEXT_PAGE_TOKEN:
		return page + 1, 0
	return page, selection


def _item_at_page(items: list[tuple[str, str]], page: int, selection: int) -> tuple[str, str] | None:
	if selection < 1:
		return None
	index = page * PAGE_SIZE + (selection - 1)
	if index >= len(items):
		return None
	return items[index]


def _county_items() -> list[tuple[str, str]]:
	return [(str(c.external_id), c.name.title()) for c in County.objects.order_by("name")]


def _subcounty_items(county_external_id: str) -> list[tuple[str, str]]:
	qs = SubCounty.objects.filter(county__external_id=int(county_external_id)).order_by("name")
	return [(str(s.external_id), s.name) for s in qs]


def _constituency_items(subcounty_external_id: str) -> list[tuple[str, str]]:
	qs = Constituency.objects.filter(subcounty__external_id=int(subcounty_external_id)).order_by("name")
	return [(str(c.external_id), c.name) for c in qs]


def _ward_items(constituency_external_id: str) -> list[tuple[str, str]]:
	qs = Ward.objects.filter(constituency__external_id=int(constituency_external_id)).order_by("name")
	return [(str(w.external_id), w.name) for w in qs]


def geography_data_loaded() -> bool:
	return County.objects.exists() and Ward.objects.exists()


def county_prompt(steps: list[str]) -> str:
	items = _county_items()
	if not items:
		return "CON Geography data loading. Enter 4-digit ward code:"
	page, selection = _parse_page_selection(steps)
	if selection == 0:
		return _paginated_menu(items, page, "Select County:")
	chosen = _item_at_page(items, page, selection)
	if not chosen:
		return _paginated_menu(items, page, "Invalid. Select County:")
	return f"CON County: {chosen[1]}\nConfirm 1. Yes 2. Back"


def county_selected(steps: list[str]) -> str | None:
	items = _county_items()
	page, selection = _parse_page_selection(steps)
	chosen = _item_at_page(items, page, selection)
	return chosen[0] if chosen else None


def subcounty_prompt(county_external_id: str, steps: list[str]) -> str:
	items = _subcounty_items(county_external_id)
	if not items:
		return "CON No subcounties found. Dial again."
	page, selection = _parse_page_selection(steps)
	if selection == 0:
		return _paginated_menu(items, page, "Select Sub-County:")
	return "CON Sub-County selected. Continue."


def subcounty_selected(county_external_id: str, steps: list[str]) -> str | None:
	items = _subcounty_items(county_external_id)
	page, selection = _parse_page_selection(steps)
	chosen = _item_at_page(items, page, selection)
	return chosen[0] if chosen else None


def constituency_prompt(subcounty_external_id: str, steps: list[str]) -> str:
	items = _constituency_items(subcounty_external_id)
	page, selection = _parse_page_selection(steps)
	if selection == 0:
		return _paginated_menu(items, page, "Select Constituency:")
	return "CON Constituency selected."


def constituency_selected(subcounty_external_id: str, steps: list[str]) -> str | None:
	items = _constituency_items(subcounty_external_id)
	page, selection = _parse_page_selection(steps)
	chosen = _item_at_page(items, page, selection)
	return chosen[0] if chosen else None


def ward_prompt(constituency_external_id: str, steps: list[str]) -> str:
	items = _ward_items(constituency_external_id)
	page, selection = _parse_page_selection(steps)
	if selection == 0:
		return _paginated_menu(items, page, "Select Ward:")
	return "CON Ward selected."


def ward_selected(constituency_external_id: str, steps: list[str]) -> str | None:
	items = _ward_items(constituency_external_id)
	page, selection = _parse_page_selection(steps)
	chosen = _item_at_page(items, page, selection)
	return chosen[0] if chosen else None


def resolve_ward(external_id: str) -> Ward | None:
	return Ward.objects.filter(external_id=int(external_id)).select_related(
		"constituency", "subcounty", "subcounty__county"
	).first()
