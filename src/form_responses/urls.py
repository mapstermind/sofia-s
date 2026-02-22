from django.urls import path

from . import views

app_name = "form_responses"

urlpatterns = [
    path("responses/", views.form_responses_view, name="form_responses"),
]
