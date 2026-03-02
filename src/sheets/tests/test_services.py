from unittest.mock import patch

import pytest

from sheets.models import FormResponse, Spreadsheet
from sheets.services import GoogleSheetsService


@pytest.fixture
def spreadsheet(db):
    return Spreadsheet.objects.create(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_name="Sheet1",
    )


@pytest.mark.django_db
def test_sync_creates_responses(spreadsheet):
    service = GoogleSheetsService()
    mock_rows = [
        ["Name", "Email", "Message"],
        ["Alice", "alice@example.com", "Hello"],
        ["Bob", "bob@example.com", "World"],
    ]
    with patch.object(service, "get_sheet_data", return_value=mock_rows):
        result = service.sync_spreadsheet(spreadsheet)

    assert result["rows_synced"] == 2
    assert result["rows_created"] == 2
    assert result["rows_updated"] == 0
    assert result["errors"] == []
    assert FormResponse.objects.count() == 2


@pytest.mark.django_db
def test_sync_updates_existing(spreadsheet):
    FormResponse.objects.create(
        spreadsheet=spreadsheet,
        row_index=2,
        data={"Name": "Old Alice", "Email": ""},
    )
    service = GoogleSheetsService()
    mock_rows = [
        ["Name", "Email"],
        ["New Alice", "new@example.com"],
    ]
    with patch.object(service, "get_sheet_data", return_value=mock_rows):
        result = service.sync_spreadsheet(spreadsheet)

    assert result["rows_created"] == 0
    assert result["rows_updated"] == 1
    row = FormResponse.objects.get(spreadsheet=spreadsheet, row_index=2)
    assert row.data["Name"] == "New Alice"


@pytest.mark.django_db
def test_sync_handles_empty_sheet(spreadsheet):
    service = GoogleSheetsService()
    with patch.object(service, "get_sheet_data", return_value=[]):
        result = service.sync_spreadsheet(spreadsheet)

    assert result["rows_synced"] == 0
    assert result["errors"] == []


@pytest.mark.django_db
def test_sync_handles_short_rows(spreadsheet):
    """Rows shorter than the header should be padded with empty strings."""
    service = GoogleSheetsService()
    mock_rows = [
        ["Name", "Email", "Phone"],
        ["Alice", "alice@example.com"],  # Missing Phone
    ]
    with patch.object(service, "get_sheet_data", return_value=mock_rows):
        result = service.sync_spreadsheet(spreadsheet)

    assert result["errors"] == []
    row = FormResponse.objects.get(row_index=2)
    assert row.data["Phone"] == ""


@pytest.mark.django_db
def test_sync_records_error_on_exception(spreadsheet):
    service = GoogleSheetsService()
    with patch.object(service, "get_sheet_data", side_effect=RuntimeError("API down")):
        result = service.sync_spreadsheet(spreadsheet)

    assert len(result["errors"]) == 1
    assert "API down" in result["errors"][0]
