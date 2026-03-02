import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from core.decorators import staff_required

from .models import FormResponse, Spreadsheet


@staff_required
def spreadsheet_list(request: HttpRequest) -> HttpResponse:
    spreadsheets = Spreadsheet.objects.all().order_by("-created_at")
    return render(request, "sheets/spreadsheet_list.html", {"spreadsheets": spreadsheets})


@staff_required
def spreadsheet_detail(request: HttpRequest, pk: int) -> HttpResponse:
    spreadsheet = get_object_or_404(Spreadsheet, pk=pk)
    responses = FormResponse.objects.filter(spreadsheet=spreadsheet).order_by("row_index")

    first = responses.first()
    headers = list(first.data.keys()) if first else []

    responses_with_values = [
        (r, [r.data.get(h, "") for h in headers]) for r in responses
    ]

    chart_data_json = json.dumps(
        {"total": responses.count(), "headers": headers},
        cls=DjangoJSONEncoder,
    )

    return render(
        request,
        "sheets/spreadsheet_detail.html",
        {
            "spreadsheet": spreadsheet,
            "responses_with_values": responses_with_values,
            "headers": headers,
            "total_responses": responses.count(),
            "chart_data_json": chart_data_json,
        },
    )


@staff_required
def dashboard(request: HttpRequest) -> HttpResponse:
    from django.db.models import Count

    spreadsheets = (
        Spreadsheet.objects.filter(is_active=True)
        .annotate(response_count=Count("responses"))
        .order_by("-created_at")
    )
    total_responses = FormResponse.objects.count()

    chart_data = {
        "labels": [ss.title for ss in spreadsheets],
        "datasets": [
            {
                "label": "Responses",
                "data": [ss.response_count for ss in spreadsheets],
                "backgroundColor": "rgba(54, 162, 235, 0.5)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
            }
        ],
    }
    chart_data_json = json.dumps(chart_data, cls=DjangoJSONEncoder)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "spreadsheets": spreadsheets,
            "total_responses": total_responses,
            "chart_data_json": chart_data_json,
        },
    )
