import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def safe_int(val, default=1):
    """
    Safely converts a value to int. Returns default if val is None, empty string,
    'undefined', 'null', or invalid.
    """
    if val is None:
        return default
    try:
        val_str = str(val).strip()
        if not val_str or val_str in ("undefined", "null", "None"):
            return default
        return int(val_str)
    except (ValueError, TypeError):
        return default


def parse_request_data(request):
    """
    Parses request payload or parameters into a Python dict.
    - GET request: query params (request.GET)
    - POST/PUT/PATCH with JSON: parsed JSON body
    - POST/PUT/PATCH with form: request.POST
    """
    if request.method == "GET":
        return dict(request.GET.items())
    if (request.content_type and "application/json" in request.content_type) or (request.body and not request.POST):
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            return {}
    if request.POST:
        return dict(request.POST.items())
    return {}


def json_response(payload, status=200):
    if isinstance(payload, tuple):
        res, st = payload
        return JsonResponse(res, status=st, safe=False)
    return JsonResponse(payload, status=status, safe=False)


class JsonExceptionMiddleware:
    """
    Middleware that catches unhandled exceptions in views and returns
    a clean JSON error response instead of standard HTML error pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "message": f"Server error: {str(exception)}"
        }, status=500)
