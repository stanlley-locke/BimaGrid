"""Shared DRF permission classes."""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.accounts.models import Profile


def _profile_role(user) -> str:
	if not user or not user.is_authenticated:
		return ""
	profile = getattr(user, "profile", None)
	if user.is_staff or getattr(profile, "role", "") == Profile.Role.ADMIN:
		return Profile.Role.ADMIN
	return getattr(profile, "role", Profile.Role.CUSTOMER)


class HasRole(BasePermission):
	"""Base permission that checks the user's profile role against allowed_roles."""

	allowed_roles: set[str] = set()

	def has_permission(self, request, view) -> bool:
		if not request.user or not request.user.is_authenticated:
			return False
		if request.user.is_staff:
			return True
		return _profile_role(request.user) in self.allowed_roles


class IsAdminUser(BasePermission):
	def has_permission(self, request, view) -> bool:
		return bool(
			request.user
			and request.user.is_authenticated
			and (
				request.user.is_staff
				or _profile_role(request.user) == Profile.Role.ADMIN
			)
		)


class IsBrokerOrAdmin(BasePermission):
	def has_permission(self, request, view) -> bool:
		if not request.user or not request.user.is_authenticated:
			return False
		if request.user.is_staff:
			return True
		return _profile_role(request.user) in {Profile.Role.ADMIN, Profile.Role.BROKER}


class IsFarmerOrAbove(BasePermission):
	"""Farmers, brokers, and admins may access farmer-facing endpoints."""

	def has_permission(self, request, view) -> bool:
		if not request.user or not request.user.is_authenticated:
			return False
		if request.user.is_staff:
			return True
		return _profile_role(request.user) in {
			Profile.Role.ADMIN,
			Profile.Role.BROKER,
			Profile.Role.FARMER,
			Profile.Role.CUSTOMER,
		}


class IsAdminOrReadOnly(BasePermission):
	def has_permission(self, request, view) -> bool:
		if request.method in ("GET", "HEAD", "OPTIONS"):
			return bool(request.user and request.user.is_authenticated)
		return IsAdminUser().has_permission(request, view)
