from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

	initial = True

	dependencies = [
		("accounts", "0001_initial"),
	]

	operations = [
		migrations.CreateModel(
			name="FarmerOnboarding",
			fields=[
				("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("ward_code", models.CharField(blank=True, max_length=32)),
				("crop", models.CharField(blank=True, choices=[("maize", "Maize"), ("beans", "Beans"), ("sorghum", "Sorghum"), ("wheat", "Wheat"), ("rice", "Rice"), ("coffee", "Coffee"), ("tea", "Tea"), ("potato", "Potato"), ("mixed", "Mixed Crops")], max_length=32)),
				("acreage", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
				("mpesa_number", models.CharField(blank=True, max_length=32)),
				("verification_level", models.PositiveSmallIntegerField(default=1)),
				("status", models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted"), ("under_review", "Under Review"), ("verified", "Verified"), ("rejected", "Rejected")], default="draft", max_length=16)),
				("notes", models.TextField(blank=True)),
				("submitted_at", models.DateTimeField(blank=True, null=True)),
				("approved_at", models.DateTimeField(blank=True, null=True)),
				("rejection_reason", models.TextField(blank=True)),
				(
					"profile",
					models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="onboarding", to="accounts.profile"),
				),
			],
			options={"ordering": ["-updated_at"]},
		),
		migrations.CreateModel(
			name="LandParcel",
			fields=[
				("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("name", models.CharField(blank=True, max_length=255)),
				("ward_code", models.CharField(blank=True, max_length=32)),
				("h3_index", models.CharField(db_index=True, max_length=32)),
				("geometry_geojson", models.JSONField(default=dict)),
				("ownership_docs", models.JSONField(blank=True, default=list)),
				("acreage", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
				("is_primary", models.BooleanField(default=False)),
				("verified", models.BooleanField(default=False)),
				(
					"onboarding",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="land_parcels", to="onboarding.farmeronboarding"),
				),
			],
			options={"ordering": ["-is_primary", "name", "created_at"]},
		),
		migrations.AddIndex(
			model_name="landparcel",
			index=models.Index(fields=["h3_index"], name="onboarding_l_h3_ind_5b8d56_idx"),
		),
	]