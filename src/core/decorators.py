from collections.abc import Callable
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

ViewFunc = Callable[..., HttpResponse]


def staff_required(view_func: ViewFunc) -> ViewFunc:
    """Require the user to be logged in and have is_staff=True."""

    @login_required
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper  # type: ignore[return-value]
