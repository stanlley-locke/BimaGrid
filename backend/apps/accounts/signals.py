"""Account signals — profile creation is handled by registration and get_or_create_profile."""

from __future__ import annotations

# Intentionally empty: auto-creating profiles on User save conflicts with explicit
# Profile.objects.create() in tests and registration flows.
