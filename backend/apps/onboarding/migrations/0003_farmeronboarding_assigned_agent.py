"""Add assigned_agent FK for broker/agent scoping."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
	dependencies = [
		("accounts", "0001_initial"),
		("onboarding", "0002_rename_onboarding_l_h3_ind_5b8d56_idx_onboarding__h3_inde_ca6593_idx"),
	]

	operations = [
		migrations.AddField(
			model_name="farmeronboarding",
			name="assigned_agent",
			field=models.ForeignKey(
				blank=True,
				limit_choices_to={"role": "broker"},
				null=True,
				on_delete=django.db.models.deletion.SET_NULL,
				related_name="assigned_onboardings",
				to="accounts.profile",
			),
		),
		migrations.AddIndex(
			model_name="farmeronboarding",
			index=models.Index(fields=["assigned_agent"], name="onboarding__assigned_7a1b2c_idx"),
		),
	]
