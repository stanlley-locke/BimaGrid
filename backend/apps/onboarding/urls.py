"""Onboarding URLs."""

from django.urls import path

from . import views


urlpatterns = [
	path("", views.CurrentOnboardingView.as_view(), name="onboarding-current"),
	path("submit/", views.SubmitOnboardingView.as_view(), name="onboarding-submit"),
]
