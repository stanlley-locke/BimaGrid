"""Claims API views."""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Claim
from .serializers import ClaimSerializer


class ClaimViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ClaimSerializer

	def get_queryset(self):
		return Claim.objects.select_related("policy", "policy__onboarding", "policy__onboarding__profile").prefetch_related("reviews").all()
