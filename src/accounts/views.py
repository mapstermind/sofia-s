from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .emails import send_login_email
from .forms import EmailLoginForm
from .models import LoginToken


def login_request(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                token = LoginToken.create_for_user(user)
                send_login_email(request, token)
            except User.DoesNotExist:
                # Don't reveal whether the email is registered
                pass
            return redirect("accounts:login_sent")
    else:
        form = EmailLoginForm()
    return render(request, "registration/login.html", {"form": form})


def login_sent(request: HttpRequest) -> HttpResponse:
    return render(request, "registration/login_sent.html")


def login_verify(request: HttpRequest) -> HttpResponse:
    token_value = request.GET.get("token", "")

    try:
        token = LoginToken.objects.select_related("user").get(token=token_value)
    except LoginToken.DoesNotExist:
        return render(
            request,
            "accounts/login_verify_invalid.html",
            {"error": "Invalid login link."},
        )

    if not token.is_valid:
        return render(
            request,
            "accounts/login_verify_invalid.html",
            {"error": "This link has expired or has already been used."},
        )

    token.is_used = True
    token.save(update_fields=["is_used"])
    login(request, token.user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect(settings.LOGIN_REDIRECT_URL)


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("accounts:login")
