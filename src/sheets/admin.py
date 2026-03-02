from django.contrib import admin, messages

from .models import FormResponse, Spreadsheet
from .services import GoogleSheetsService


@admin.register(Spreadsheet)
class SpreadsheetAdmin(admin.ModelAdmin):
    list_display = ["title", "spreadsheet_id", "is_active", "last_synced_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["title", "spreadsheet_id"]
    actions = ["sync_sheets"]

    @admin.action(description="Sync selected spreadsheets from Google Sheets")
    def sync_sheets(self, request, queryset):
        service = GoogleSheetsService()
        for spreadsheet in queryset:
            result = service.sync_spreadsheet(spreadsheet)
            if result["errors"]:
                self.message_user(
                    request,
                    f"Error syncing '{spreadsheet.title}': {result['errors'][0]}",
                    messages.ERROR,
                )
            else:
                self.message_user(
                    request,
                    (
                        f"Synced '{spreadsheet.title}': {result['rows_synced']} rows "
                        f"({result['rows_created']} new, {result['rows_updated']} updated)"
                    ),
                    messages.SUCCESS,
                )


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ["spreadsheet", "row_index", "submitted_at", "synced_at"]
    list_filter = ["spreadsheet"]
    raw_id_fields = ["spreadsheet"]
    readonly_fields = ["synced_at"]
