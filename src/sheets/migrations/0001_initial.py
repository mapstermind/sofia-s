import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Spreadsheet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spreadsheet_id", models.CharField(max_length=100, unique=True)),
                ("title", models.CharField(max_length=200)),
                (
                    "sheet_name",
                    models.CharField(default="Form Responses 1", max_length=100),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="FormResponse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("row_index", models.PositiveIntegerField()),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("data", models.JSONField()),
                ("synced_at", models.DateTimeField(auto_now=True)),
                (
                    "spreadsheet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="responses",
                        to="sheets.spreadsheet",
                    ),
                ),
            ],
            options={
                "ordering": ["row_index"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="formresponse",
            unique_together={("spreadsheet", "row_index")},
        ),
    ]
