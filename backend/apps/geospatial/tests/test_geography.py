"""Geography API and load command tests."""

from django.core.management import call_command
from django.test import Client, TestCase
from pathlib import Path

from apps.geospatial.models import Constituency, County, SubCounty, Ward


class GeographyAPITests(TestCase):
	def setUp(self):
		self.client = Client()
		self.county = County.objects.create(external_id=12, name="MERU")
		self.subcounty = SubCounty.objects.create(
			external_id=120, county=self.county, name="Imenti North"
		)
		self.constituency = Constituency.objects.create(
			external_id=1200, subcounty=self.subcounty, name="Imenti North"
		)
		self.ward = Ward.objects.create(
			external_id=501,
			constituency=self.constituency,
			subcounty=self.subcounty,
			name="Ntima East",
		)

	def test_list_counties(self):
		response = self.client.get("/api/v1/geography/counties/")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.json()), 1)
		self.assertEqual(response.json()[0]["name"], "MERU")

	def test_county_subcounties(self):
		url = f"/api/v1/geography/counties/{self.county.id}/subcounties/"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()[0]["name"], "Imenti North")

	def test_subcounty_constituencies(self):
		url = f"/api/v1/geography/subcounties/{self.subcounty.id}/constituencies/"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.json()), 1)

	def test_wards_filter(self):
		response = self.client.get(
			"/api/v1/geography/wards/",
			{"constituency_id": str(self.constituency.id)},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()[0]["name"], "Ntima East")
		self.assertEqual(response.json()[0]["ward_code"], "0501")


class LoadKenyaAdminBoundariesTests(TestCase):
	def test_load_from_json(self):
		json_path = Path(__file__).resolve().parents[4] / "Kenya_counties_subcounties_constituencies_wards.json"
		if not json_path.exists():
			self.skipTest("Kenya JSON dataset not available in repo")

		call_command("load_kenya_admin_boundaries", f"--json-path={json_path}", "--clear")
		self.assertEqual(County.objects.count(), 47)
		self.assertGreater(Ward.objects.count(), 1000)
