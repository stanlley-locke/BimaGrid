"""Account Celery tasks."""

from __future__ import annotations

from celery import shared_task

from integrations.iprs import IPRSClient

from .models import Profile


@shared_task
def verify_identity_async(profile_id: str, id_number: str, first_name: str, last_name: str, dob: str) -> dict:
	profile = Profile.objects.get(id=profile_id)
	result = IPRSClient().verify_identity(id_number, first_name, last_name, dob)
	profile.national_id = id_number
	if result.get("status") == "verified":
		profile.is_phone_verified = True
	profile.save(update_fields=["national_id", "is_phone_verified", "updated_at"])
	return result
