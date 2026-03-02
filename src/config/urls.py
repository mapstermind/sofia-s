from django.contrib import admin
from django.urls import include, path

from core.views import root_redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_redirect, name="root"),
    path("", include("core.urls")),
    path("", include("accounts.urls")),
    path("", include("sheets.urls")),
    path("api/", include("api.urls")),
]
