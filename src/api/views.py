import csv
from io import StringIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from sheets.models import FormResponse, Spreadsheet


class StaffRequiredMixin(LoginRequiredMixin):
    """Mixin that requires is_staff=True; raises 403 for authenticated non-staff."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SpreadsheetListView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        data = list(
            Spreadsheet.objects.filter(is_active=True)
            .annotate(response_count=Count("responses"))
            .values(
                "id",
                "spreadsheet_id",
                "title",
                "sheet_name",
                "response_count",
                "last_synced_at",
                "created_at",
            )
        )
        return JsonResponse(data, safe=False, encoder=DjangoJSONEncoder)


class SpreadsheetDetailView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        spreadsheet = get_object_or_404(Spreadsheet, pk=pk)
        responses = FormResponse.objects.filter(spreadsheet=spreadsheet).order_by(
            "row_index"
        )

        if request.GET.get("format") == "csv":
            return self._csv_response(spreadsheet, responses)

        data = {
            "id": spreadsheet.pk,
            "spreadsheet_id": spreadsheet.spreadsheet_id,
            "title": spreadsheet.title,
            "sheet_name": spreadsheet.sheet_name,
            "last_synced_at": spreadsheet.last_synced_at,
            "responses": [
                {
                    "row_index": r.row_index,
                    "submitted_at": r.submitted_at,
                    "data": r.data,
                    "synced_at": r.synced_at,
                }
                for r in responses
            ],
        }
        return JsonResponse(data, encoder=DjangoJSONEncoder)

    def _csv_response(self, spreadsheet: Spreadsheet, responses) -> HttpResponse:
        output = StringIO()
        writer = csv.writer(output)

        responses_list = list(responses)
        if responses_list:
            headers = list(responses_list[0].data.keys())
            writer.writerow(["row_index", "submitted_at", *headers])
            for r in responses_list:
                writer.writerow(
                    [r.row_index, r.submitted_at or "", *(r.data.get(h, "") for h in headers)]
                )
        else:
            writer.writerow(["No data available"])

        filename = spreadsheet.title.replace(" ", "_") + ".csv"
        response = HttpResponse(
            output.getvalue(), content_type="text/csv; charset=utf-8-sig"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DashboardStatsView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        stats = {
            "total_spreadsheets": Spreadsheet.objects.filter(is_active=True).count(),
            "total_responses": FormResponse.objects.count(),
            "spreadsheets": list(
                Spreadsheet.objects.filter(is_active=True)
                .annotate(response_count=Count("responses"))
                .values("id", "title", "response_count", "last_synced_at")
            ),
        }
        return JsonResponse(stats, encoder=DjangoJSONEncoder)
