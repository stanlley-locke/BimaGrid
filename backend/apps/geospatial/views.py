"""Geospatial API views."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.queryset import scope_onboarding_queryset

from .models import ParcelGeometry
from .serializers import ParcelGeometrySerializer


class ParcelGeometryViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ParcelGeometrySerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields = ["h3_index", "ward_code", "source"]
	search_fields = ["name", "h3_index", "ward_code"]
	ordering_fields = ["created_at", "acreage"]

	def get_queryset(self):
		qs = ParcelGeometry.objects.select_related(
			"onboarding", "onboarding__profile", "onboarding__assigned_agent"
		)
		return scope_onboarding_queryset(qs, self.request.user)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def h3_index_view(request):
	lat = request.GET.get("lat")
	lng = request.GET.get("lng")
	resolution = request.GET.get("resolution", 9)
	if lat and lng:
		import h3

		try:
			# h3-py version 4 API
			index = h3.latlng_to_cell(float(lat), float(lng), int(resolution))
			return Response({"h3_index": index})
		except AttributeError:
			# fallback for older versions
			try:
				index = h3.geo_to_h3(float(lat), float(lng), int(resolution))
				return Response({"h3_index": index})
			except Exception as e:
				return Response({"error": str(e)}, status=400)
		except Exception as e:
			return Response({"error": str(e)}, status=400)
	return Response({"error": "Missing lat or lng"}, status=400)
