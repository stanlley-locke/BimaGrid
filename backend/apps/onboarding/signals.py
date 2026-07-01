"""Onboarding signals."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Profile

from .models import FarmerOnboarding


@receiver(post_save, sender=Profile)
def create_onboarding_for_profile(sender, instance: Profile, created: bool, **kwargs):
	if created:
		FarmerOnboarding.objects.get_or_create(profile=instance)
