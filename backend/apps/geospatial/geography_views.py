"""Kenya admin geography API views for USSD drill-down."""

from __future__ import annotations

from rest_framework import generics, permissions

from .models import Constituency, County, SubCounty, Ward
from .serializers import ConstituencySerializer, CountySerializer, SubCountySerializer, WardSerializer


class CountyListView(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	queryset = County.objects.all()
	serializer_class = CountySerializer


class CountySubCountyListView(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = SubCountySerializer

	def get_queryset(self):
		return SubCounty.objects.filter(county_id=self.kwargs["county_id"]).select_related("county")


class SubCountyConstituencyListView(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = ConstituencySerializer

	def get_queryset(self):
		return Constituency.objects.filter(
			subcounty_id=self.kwargs["subcounty_id"]
		).select_related("subcounty")


class WardListView(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = WardSerializer

	def get_queryset(self):
		qs = Ward.objects.select_related("constituency", "subcounty", "subcounty__county")
		constituency_id = self.request.query_params.get("constituency_id")
		subcounty_id = self.request.query_params.get("subcounty_id")
		if constituency_id:
			qs = qs.filter(constituency_id=constituency_id)
		if subcounty_id:
			qs = qs.filter(subcounty_id=subcounty_id)
		return qs
