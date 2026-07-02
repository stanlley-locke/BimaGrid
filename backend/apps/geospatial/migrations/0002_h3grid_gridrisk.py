# Generated migration for H3Grid and GridRisk models

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

	dependencies = [
		("geospatial", "0001_initial"),
	]

	operations = [
		migrations.CreateModel(
			name="H3Grid",
			fields=[
				("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("resolution", models.PositiveSmallIntegerField(default=9)),
				("h3_index", models.CharField(db_index=True, max_length=32, unique=True)),
				("centroid_lat", models.DecimalField(decimal_places=6, max_digits=9)),
				("centroid_lng", models.DecimalField(decimal_places=6, max_digits=9)),
				("boundary_geojson", models.JSONField(blank=True, default=dict)),
				("region_code", models.CharField(blank=True, max_length=32)),
			],
			options={
				"ordering": ["h3_index"],
			},
		),
		migrations.CreateModel(
			name="GridRisk",
			fields=[
				("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("h3_index", models.CharField(db_index=True, max_length=32)),
				("mean_rainfall_mm", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
				("flood_threshold_mm", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
				("frost_days", models.PositiveIntegerField(default=0)),
				("heat_stress_days", models.PositiveIntegerField(default=0)),
				("drought_risk_score", models.DecimalField(decimal_places=4, default=0, max_digits=6)),
				("flood_risk_score", models.DecimalField(decimal_places=4, default=0, max_digits=6)),
				("metadata", models.JSONField(blank=True, default=dict)),
			],
			options={
				"ordering": ["h3_index"],
			},
		),
		migrations.AddIndex(
			model_name="h3grid",
			index=models.Index(fields=["resolution", "h3_index"], name="geospatial__resolut_6a8b2a_idx"),
		),
		migrations.AddIndex(
			model_name="gridrisk",
			index=models.Index(fields=["h3_index"], name="geospatial__h3_inde_4c9f1d_idx"),
		),
		migrations.AlterUniqueTogether(
			name="gridrisk",
			unique_together={("h3_index",)},
		),
	]
