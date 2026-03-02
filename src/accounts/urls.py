from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_request, name="login"),
    path("login/sent/", views.login_sent, name="login_sent"),
    path("login/verify/", views.login_verify, name="login_verify"),
    path("logout/", views.logout_view, name="logout"),
]
