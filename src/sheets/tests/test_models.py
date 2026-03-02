import pytest
from django.db import IntegrityError

from sheets.models import FormResponse, Spreadsheet


@pytest.fixture
def spreadsheet(db):
    return Spreadsheet.objects.create(
        spreadsheet_id="abc123",
        title="My Test Sheet",
    )


@pytest.mark.django_db
def test_spreadsheet_defaults(spreadsheet):
    assert spreadsheet.sheet_name == "Form Responses 1"
    assert spreadsheet.is_active is True
    assert spreadsheet.last_synced_at is None


@pytest.mark.django_db
def test_spreadsheet_str(spreadsheet):
    assert str(spreadsheet) == "My Test Sheet"


@pytest.mark.django_db
def test_form_response_creation(spreadsheet):
    r = FormResponse.objects.create(
        spreadsheet=spreadsheet,
        row_index=2,
        data={"Name": "Alice", "Email": "alice@example.com"},
    )
    assert r.row_index == 2
    assert r.data["Name"] == "Alice"


@pytest.mark.django_db
def test_form_response_unique_constraint(spreadsheet):
    FormResponse.objects.create(spreadsheet=spreadsheet, row_index=2, data={"x": "1"})
    with pytest.raises(IntegrityError):
        FormResponse.objects.create(spreadsheet=spreadsheet, row_index=2, data={"x": "2"})


@pytest.mark.django_db
def test_form_response_str(spreadsheet):
    r = FormResponse.objects.create(spreadsheet=spreadsheet, row_index=3, data={})
    assert "3" in str(r)
    assert "My Test Sheet" in str(r)
