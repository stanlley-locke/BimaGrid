"""Role-based queryset scoping helpers for DRF viewsets."""

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.accounts.models import Profile


def user_role(user) -> str:
	if not user or not user.is_authenticated:
		return ""
	profile = getattr(user, "profile", None)
	if user.is_staff or getattr(profile, "role", "") == Profile.Role.ADMIN:
		return Profile.Role.ADMIN
	return getattr(profile, "role", Profile.Role.CUSTOMER)


def is_admin(user) -> bool:
	return user_role(user) == Profile.Role.ADMIN


def is_broker(user) -> bool:
	return user_role(user) == Profile.Role.BROKER


def scope_onboarding_queryset(queryset: QuerySet, user, prefix: str = "") -> QuerySet:
	"""Scope querysets keyed by FarmerOnboarding (directly or via FK prefix)."""
	if is_admin(user):
		return queryset
	profile = user.profile
	field = f"{prefix}profile" if prefix else "profile"
	if is_broker(user):
		agent_field = f"{prefix}assigned_agent" if prefix else "assigned_agent"
		return queryset.filter(**{agent_field: profile})
	return queryset.filter(**{field: profile})


def scope_policy_queryset(queryset: QuerySet, user, via_policy: bool = False) -> QuerySet:
	"""Scope Policy querysets or models linked through Policy FK."""
	if is_admin(user):
		return queryset
	profile = user.profile
	if via_policy:
		prefix = "policy__onboarding__"
	else:
		prefix = "onboarding__"
	if is_broker(user):
		return queryset.filter(**{f"{prefix}assigned_agent": profile})
	return queryset.filter(**{f"{prefix}profile": profile})


def scope_profile_queryset(queryset: QuerySet, user) -> QuerySet:
	if is_admin(user):
		return queryset
	profile = user.profile
	if is_broker(user):
		return queryset.filter(Q(onboarding__assigned_agent=profile) | Q(pk=profile.pk))
	return queryset.filter(pk=profile.pk)


def scope_user_queryset(queryset: QuerySet, user) -> QuerySet:
	if is_admin(user):
		return queryset
	return queryset.filter(user=user)


def scope_h3_queryset(queryset: QuerySet, user, h3_field: str = "h3_index") -> QuerySet:
	"""Scope satellite/oracle data to H3 cells covering the user's parcels."""
	if is_admin(user):
		return queryset
	from apps.onboarding.models import LandParcel

	profile = user.profile
	if is_broker(user):
		parcel_filter = Q(onboarding__assigned_agent=profile)
	else:
		parcel_filter = Q(onboarding__profile=profile)
	h3_indexes = LandParcel.objects.filter(parcel_filter).values_list("h3_index", flat=True).distinct()
	if not h3_indexes:
		return queryset.none()
	return queryset.filter(**{f"{h3_field}__in": h3_indexes})
