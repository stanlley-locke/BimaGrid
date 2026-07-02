"""Spatial query helpers (JSONField + H3 indexing)."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Q

from .h3_utils import k_ring_indices
from .models import GridRisk, H3Grid, ParcelGeometry


def find_parcels_by_h3(h3_index: str) -> list[ParcelGeometry]:
	indices = k_ring_indices(h3_index, k=0)
	return list(ParcelGeometry.objects.filter(h3_index__in=indices))


def find_nearby_grid_risks(h3_index: str, ring: int = 1) -> list[GridRisk]:
	indices = k_ring_indices(h3_index, k=ring)
	return list(GridRisk.objects.filter(h3_index__in=indices))


def get_grid_risk(h3_index: str) -> GridRisk | None:
	return GridRisk.objects.filter(h3_index=h3_index).first()


def find_h3_grids_for_region(region_code: str) -> list[H3Grid]:
	return list(H3Grid.objects.filter(region_code=region_code))


def average_risk_score(h3_index: str, ring: int = 1) -> Decimal:
	risks = find_nearby_grid_risks(h3_index, ring=ring)
	if not risks:
		return Decimal("0.5")
	total = sum(risk.drought_risk_score for risk in risks)
	return (total / len(risks)).quantize(Decimal("0.0001"))


def parcels_in_ward(ward_code: str) -> list[ParcelGeometry]:
	query = Q(ward_code=ward_code)
	if ward_code:
		return list(ParcelGeometry.objects.filter(query))
	return []
