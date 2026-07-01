from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

	initial = True

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name="Profile",
			fields=[
				("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("full_name", models.CharField(blank=True, max_length=255)),
				("phone_number", models.CharField(blank=True, max_length=32)),
				("national_id", models.CharField(blank=True, max_length=64)),
				("role", models.CharField(choices=[("customer", "Customer"), ("farmer", "Farmer"), ("broker", "Broker"), ("admin", "Admin")], default="customer", max_length=16)),
				("preferred_language", models.CharField(choices=[("en", "English"), ("sw", "Swahili")], default="en", max_length=8)),
				("is_phone_verified", models.BooleanField(default=False)),
				(
					"user",
					models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL),
				),
			],
			options={
				"ordering": ["full_name", "user__username"],
			},
		),
		migrations.AddIndex(
			model_name="profile",
			index=models.Index(fields=["phone_number"], name="accounts_pr_phone_n_3f4f97_idx"),
		),
		migrations.AddIndex(
			model_name="profile",
			index=models.Index(fields=["national_id"], name="accounts_pr_national_7f72d5_idx"),
		),
	]