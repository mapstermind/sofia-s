import pytest
from django.contrib.auth.models import User

from sheets.models import FormResponse, Spreadsheet


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff@example.com",
        email="staff@example.com",
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="user@example.com",
        email="user@example.com",
    )


@pytest.fixture
def spreadsheet(db):
    return Spreadsheet.objects.create(
        spreadsheet_id="test_spreadsheet_id_abc123",
        title="Test Spreadsheet",
        sheet_name="Sheet1",
    )


@pytest.fixture
def form_response(db, spreadsheet):
    return FormResponse.objects.create(
        spreadsheet=spreadsheet,
        row_index=2,
        data={"Name": "Test User", "Email": "test@example.com", "Message": "Hello"},
    )
