import secrets
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class LoginToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_tokens")
    # token_urlsafe(48) produces exactly 64 URL-safe base64 characters
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"LoginToken for {self.user.email}"

    @classmethod
    def create_for_user(cls, user: User) -> "LoginToken":
        return cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(48),
            expires_at=timezone.now() + timedelta(minutes=15),
        )

    @property
    def is_valid(self) -> bool:
        return not self.is_used and timezone.now() < self.expires_at
