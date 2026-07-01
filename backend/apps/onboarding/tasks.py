"""Onboarding Celery tasks."""

from celery import shared_task

from .services import refresh_onboarding_level


@shared_task
def recalculate_onboarding_level(onboarding_id: str) -> str:
	from .models import FarmerOnboarding

	onboarding = FarmerOnboarding.objects.select_related("profile").get(id=onboarding_id)
	refresh_onboarding_level(onboarding)
	return str(onboarding.id)
