from django.urls import path

from .views import DashboardStatsView, SpreadsheetDetailView, SpreadsheetListView

app_name = "api"

urlpatterns = [
    path("spreadsheets/", SpreadsheetListView.as_view(), name="spreadsheet_list"),
    path("spreadsheets/<int:pk>/", SpreadsheetDetailView.as_view(), name="spreadsheet_detail"),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard_stats"),
]
