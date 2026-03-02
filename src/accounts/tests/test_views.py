import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import LoginToken


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="staff@example.com",
        email="staff@example.com",
        is_staff=True,
    )


@pytest.mark.django_db
def test_login_page_renders(client):
    response = client.get(reverse("accounts:login"))
    assert response.status_code == 200
    assert b"Send Login Link" in response.content


@pytest.mark.django_db
def test_login_post_creates_token(client, user, mailoutbox):
    response = client.post(reverse("accounts:login"), {"email": user.email})
    assert response.status_code == 302
    assert response["Location"] == reverse("accounts:login_sent")
    assert LoginToken.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_login_post_unknown_email_still_redirects(client):
    """Security: don't reveal whether an email is registered."""
    response = client.post(reverse("accounts:login"), {"email": "nobody@example.com"})
    assert response.status_code == 302
    assert response["Location"] == reverse("accounts:login_sent")
    assert LoginToken.objects.count() == 0


@pytest.mark.django_db
def test_login_sent_page_renders(client):
    response = client.get(reverse("accounts:login_sent"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_verify_valid_token_logs_in(client, user):
    token = LoginToken.create_for_user(user)
    url = reverse("accounts:login_verify") + f"?token={token.token}"
    response = client.get(url)
    assert response.status_code == 302
    assert response["Location"] == "/dashboard/"
    token.refresh_from_db()
    assert token.is_used is True


@pytest.mark.django_db
def test_login_verify_invalid_token_shows_error(client):
    response = client.get(reverse("accounts:login_verify") + "?token=bogus")
    assert response.status_code == 200
    assert b"Invalid login link" in response.content


@pytest.mark.django_db
def test_login_verify_expired_token_shows_error(client, user):
    from datetime import timedelta

    from django.utils import timezone

    token = LoginToken.create_for_user(user)
    token.expires_at = timezone.now() - timedelta(seconds=1)
    token.save()

    response = client.get(reverse("accounts:login_verify") + f"?token={token.token}")
    assert response.status_code == 200
    assert b"expired" in response.content.lower()


@pytest.mark.django_db
def test_logout_requires_post(client, user):
    client.force_login(user)
    response = client.get(reverse("accounts:logout"))
    assert response.status_code == 405


@pytest.mark.django_db
def test_logout_post_redirects_to_login(client, user):
    client.force_login(user)
    response = client.post(reverse("accounts:logout"))
    assert response.status_code == 302
    assert response["Location"] == reverse("accounts:login")
