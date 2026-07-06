"""Admin dashboard URLs."""

from django.urls import path

from .views import AdminStatsView, BypassPaymentView, GodModeDashboardView, SimulateDroughtView, TriggerEvaluationView


urlpatterns = [
	path("", GodModeDashboardView.as_view(), name="admin-god-mode-dashboard"),
	path("simulate-drought/", SimulateDroughtView.as_view(), name="admin-simulate-drought"),
	path("trigger-evaluation/", TriggerEvaluationView.as_view(), name="admin-trigger-evaluation"),
	path("bypass-payment/", BypassPaymentView.as_view(), name="admin-bypass-payment"),
	path("stats/", AdminStatsView.as_view(), name="admin-stats"),
]
