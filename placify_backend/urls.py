from django.urls import path, include
from django.http import JsonResponse
from config.database import init_db, is_db_available

try:
    init_db()
except Exception as e:
    print(f"[DB] Startup check failed unexpectedly: {e}")

if is_db_available():
    print("=" * 60)
    print("[MODE] Using REAL MySQL database.")
    print("=" * 60)
else:
    print("=" * 60)
    print("[MODE] DB not configured/reachable — using IN-MEMORY storage.")
    print("[MODE] Data will reset when the server restarts.")
    print("=" * 60)


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "message": "Placify backend is running."
    })


urlpatterns = [
    path("", health_check),
    path("api/", include("api.urls")),
]
