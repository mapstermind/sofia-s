from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect


def health_check(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def root_redirect(request: HttpRequest) -> JsonResponse:
    return redirect("sheets:dashboard")
