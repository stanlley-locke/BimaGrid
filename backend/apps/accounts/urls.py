"""Accounts URLs for BimaGrid."""

from django.urls import path

from . import views


urlpatterns = [
	path("login/", views.LoginView.as_view(), name="accounts-login"),
	path("register/", views.RegistrationView.as_view(), name="accounts-register"),
	path("me/", views.CurrentAccountView.as_view(), name="accounts-me"),
]
