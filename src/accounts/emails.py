from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest
from django.urls import reverse

from .models import LoginToken


def send_login_email(request: HttpRequest, token: LoginToken) -> None:
    verify_url = request.build_absolute_uri(
        reverse("accounts:login_verify") + f"?token={token.token}"
    )
    subject = "Your SOFIA-S login link"
    message = (
        f"Click the link below to sign in to SOFIA-S:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in 15 minutes and can only be used once.\n\n"
        f"If you did not request this, you can safely ignore this email."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [token.user.email],
        fail_silently=False,
    )
