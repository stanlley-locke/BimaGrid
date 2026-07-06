"""USSD geography registration tests."""

from django.test import Client, TestCase

from apps.geospatial.models import Constituency, County, SubCounty, Ward


class UssdGeographyRegistrationTests(TestCase):
	def setUp(self):
		self.client = Client()
		county = County.objects.create(external_id=1, name="MOMBASA")
		subcounty = SubCounty.objects.create(external_id=1, county=county, name="Changamwe")
		constituency = Constituency.objects.create(external_id=1, subcounty=subcounty, name="Changamwe")
		Ward.objects.create(
			external_id=4,
			constituency=constituency,
			subcounty=subcounty,
			name="Changamwe",
		)

	def test_hierarchical_registration_completes(self):
		steps = [
			"1",
			"1*1",
			"1*1*1",
			"1*1*1*1",
			"1*1*1*1*1",
			"1*1*1*1*1*1",
			"1*1*1*1*1*1*2.5",
			"1*1*1*1*1*1*2.5*1",
		]
		for text in steps:
			response = self.client.post(
				"/ussd/gateway/",
				{"sessionId": "ATUid_geo", "phoneNumber": "254712345678", "text": text},
			)
			self.assertEqual(response.status_code, 200)
		self.assertTrue(response.content.decode().startswith("END Registration complete"))
