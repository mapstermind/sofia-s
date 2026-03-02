
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from sheets.models import FormResponse, Spreadsheet


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff@example.com", email="staff@example.com", is_staff=True
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="user@example.com", email="user@example.com"
    )


@pytest.fixture
def spreadsheet(db):
    return Spreadsheet.objects.create(spreadsheet_id="abc123", title="Test Sheet")


@pytest.fixture
def response_obj(db, spreadsheet):
    return FormResponse.objects.create(
        spreadsheet=spreadsheet,
        row_index=2,
        data={"Name": "Alice", "Email": "alice@example.com"},
    )


# --- SpreadsheetListView ---


@pytest.mark.django_db
def test_list_unauthenticated_redirects(client):
    response = client.get(reverse("api:spreadsheet_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_list_non_staff_forbidden(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("api:spreadsheet_list"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_list_staff_returns_json(client, staff_user, spreadsheet):
    client.force_login(staff_user)
    response = client.get(reverse("api:spreadsheet_list"))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Test Sheet"


# --- SpreadsheetDetailView ---


@pytest.mark.django_db
def test_detail_json(client, staff_user, spreadsheet, response_obj):
    client.force_login(staff_user)
    response = client.get(reverse("api:spreadsheet_detail", args=[spreadsheet.pk]))
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Sheet"
    assert len(data["responses"]) == 1


@pytest.mark.django_db
def test_detail_csv_download(client, staff_user, spreadsheet, response_obj):
    client.force_login(staff_user)
    url = reverse("api:spreadsheet_detail", args=[spreadsheet.pk]) + "?format=csv"
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv; charset=utf-8-sig"
    content = response.content.decode("utf-8-sig")
    assert "Alice" in content
    assert "Name" in content


# --- DashboardStatsView ---


@pytest.mark.django_db
def test_dashboard_stats(client, staff_user, spreadsheet, response_obj):
    client.force_login(staff_user)
    response = client.get(reverse("api:dashboard_stats"))
    assert response.status_code == 200
    data = response.json()
    assert "total_spreadsheets" in data
    assert "total_responses" in data
    assert data["total_responses"] == 1
