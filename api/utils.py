import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
