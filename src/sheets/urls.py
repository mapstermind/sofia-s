from django.urls import path

from . import views

app_name = "sheets"

urlpatterns = [
    path("spreadsheets/", views.spreadsheet_list, name="spreadsheet_list"),
    path("spreadsheets/<int:pk>/", views.spreadsheet_detail, name="spreadsheet_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
