"""Onboarding URLs."""

from django.urls import path

from . import views


urlpatterns = [
	path("", views.CurrentOnboardingView.as_view(), name="onboarding-current"),
	path("submit/", views.SubmitOnboardingView.as_view(), name="onboarding-submit"),
	path("status/", views.OnboardingStatusView.as_view(), name="onboarding-status"),
	path("verify-identity/", views.VerifyIdentityView.as_view(), name="onboarding-verify-identity"),
	path("agent-register/", views.AgentFarmerRegistrationView.as_view(), name="agent-register-farmer"),
]
