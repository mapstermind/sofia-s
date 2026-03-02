import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_check_returns_ok(client):
    response = client.get(reverse("core:health_check"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_root_redirects(client):
    response = client.get("/")
    assert response.status_code == 302
