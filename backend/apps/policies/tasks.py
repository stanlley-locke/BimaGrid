"""Policy Celery tasks."""

from __future__ import annotations

from celery import shared_task

from .models import Policy
from .services import lapse_policy


@shared_task
def expire_lapsed_policies() -> int:
	from django.utils import timezone

	today = timezone.now().date()
	count = 0
	for policy in Policy.objects.filter(status=Policy.Status.ACTIVE, coverage_end__lt=today):
		lapse_policy(policy)
		count += 1
	return count
