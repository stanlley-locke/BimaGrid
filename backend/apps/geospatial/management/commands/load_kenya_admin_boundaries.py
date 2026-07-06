"""Load Kenya administrative boundaries from the bundled JSON/SQL dataset."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geospatial.models import Constituency, County, SubCounty, Ward


def _default_dataset_path() -> Path:
	return Path(settings.BASE_DIR) / "Kenya_counties_subcounties_constituencies_wards.json"


def _read_phpmyadmin_export(path: Path) -> list:
	"""Parse phpMyAdmin JSON export (may contain trailing commas between objects)."""
	text = path.read_text(encoding="utf-8")
	text = text.replace("\n,{\"type\"", "\n{\"type\"")
	return json.loads(text)


def _parse_phpmyadmin_json(raw: list) -> dict[str, list[dict]]:
	tables: dict[str, list[dict]] = {}
	for entry in raw:
		if not isinstance(entry, dict):
			continue
		if entry.get("type") != "table":
			continue
		name = entry.get("name")
		data = entry.get("data")
		if name and isinstance(data, list):
			tables[name] = data
	return tables


class Command(BaseCommand):
	help = "Load Kenya counties, subcounties, constituencies, and wards from JSON (or SQL companion file)."

	def add_arguments(self, parser):
		parser.add_argument(
			"--json-path",
			type=str,
			default="",
			help="Path to Kenya_counties_subcounties_constituencies_wards.json",
		)
		parser.add_argument(
			"--clear",
			action="store_true",
			help="Delete existing geography rows before loading.",
		)

	def handle(self, *args, **options):
		json_path = Path(options["json_path"]) if options["json_path"] else _default_dataset_path()
		if not json_path.exists():
			self.stderr.write(self.style.ERROR(f"Dataset not found: {json_path}"))
			return

		payload = _read_phpmyadmin_export(json_path)

		tables = _parse_phpmyadmin_json(payload)
		counties_data = tables.get("counties", [])
		subcounties_data = tables.get("subcounties", [])
		stations_data = tables.get("station", [])

		if not counties_data or not subcounties_data or not stations_data:
			self.stderr.write(self.style.ERROR("JSON missing counties, subcounties, or station tables."))
			return

		with transaction.atomic():
			if options["clear"]:
				Ward.objects.all().delete()
				Constituency.objects.all().delete()
				SubCounty.objects.all().delete()
				County.objects.all().delete()

			county_map: dict[int, County] = {}
			for row in counties_data:
				external_id = int(row["county_id"])
				county, _ = County.objects.update_or_create(
					external_id=external_id,
					defaults={"name": row["county_name"].strip().upper()},
				)
				county_map[external_id] = county

			subcounty_map: dict[int, SubCounty] = {}
			for row in subcounties_data:
				external_id = int(row["subcounty_id"])
				county_id = int(row["county_id"])
				county = county_map.get(county_id)
				if not county:
					continue
				name = row["constituency_name"].strip().title()
				subcounty, _ = SubCounty.objects.update_or_create(
					external_id=external_id,
					defaults={"county": county, "name": name},
				)
				subcounty_map[external_id] = subcounty

			constituency_map: dict[tuple[int, str], Constituency] = {}
			constituency_counter = 0
			for row in stations_data:
				subcounty_id = int(row["subcounty_id"])
				constituency_name = row["constituency_name"].strip().title()
				subcounty = subcounty_map.get(subcounty_id)
				if not subcounty:
					continue
				key = (subcounty_id, constituency_name.lower())
				if key in constituency_map:
					continue
				constituency_counter += 1
				constituency, _ = Constituency.objects.update_or_create(
					external_id=constituency_counter,
					defaults={"subcounty": subcounty, "name": constituency_name},
				)
				constituency_map[key] = constituency

			ward_count = 0
			for row in stations_data:
				ward_name = row.get("ward", "").strip()
				if not ward_name:
					continue
				subcounty_id = int(row["subcounty_id"])
				constituency_name = row["constituency_name"].strip().title()
				subcounty = subcounty_map.get(subcounty_id)
				constituency = constituency_map.get((subcounty_id, constituency_name.lower()))
				if not subcounty or not constituency:
					continue
				external_id = int(row["station_id"])
				_, created = Ward.objects.update_or_create(
					external_id=external_id,
					defaults={
						"constituency": constituency,
						"subcounty": subcounty,
						"name": ward_name.title(),
					},
				)
				if created:
					ward_count += 1

		self.stdout.write(
			self.style.SUCCESS(
				f"Loaded {County.objects.count()} counties, "
				f"{SubCounty.objects.count()} subcounties, "
				f"{Constituency.objects.count()} constituencies, "
				f"{Ward.objects.count()} wards "
				f"({ward_count} new wards this run)."
			)
		)
