import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import LoginToken


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="test@example.com",
        email="test@example.com",
    )


@pytest.mark.django_db
def test_create_for_user_generates_token(user):
    token = LoginToken.create_for_user(user)
    assert token.user == user
    assert len(token.token) == 64
    assert not token.is_used
    assert token.expires_at > timezone.now()


@pytest.mark.django_db
def test_is_valid_fresh_token(user):
    token = LoginToken.create_for_user(user)
    assert token.is_valid is True


@pytest.mark.django_db
def test_is_valid_expired_token(user):
    from datetime import timedelta

    token = LoginToken.create_for_user(user)
    token.expires_at = timezone.now() - timedelta(seconds=1)
    token.save()
    assert token.is_valid is False


@pytest.mark.django_db
def test_is_valid_used_token(user):
    token = LoginToken.create_for_user(user)
    token.is_used = True
    token.save()
    assert token.is_valid is False


@pytest.mark.django_db
def test_str_representation(user):
    token = LoginToken.create_for_user(user)
    assert "test@example.com" in str(token)
