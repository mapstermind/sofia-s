from django.db import models


class Spreadsheet(models.Model):
    spreadsheet_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    sheet_name = models.CharField(max_length=100, default="Form Responses 1")
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class FormResponse(models.Model):
    spreadsheet = models.ForeignKey(
        Spreadsheet, on_delete=models.CASCADE, related_name="responses"
    )
    row_index = models.PositiveIntegerField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    data = models.JSONField()
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("spreadsheet", "row_index")
        ordering = ["row_index"]

    def __str__(self) -> str:
        return f"Response {self.row_index} for {self.spreadsheet.title}"
