"""
Notice: Placify backend has been migrated from Flask to Python Django.
To start the Django dev server, run:
    python manage.py runserver 0.0.0.0:5000
"""
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("[MIGRATION NOTICE] The backend has been migrated from Flask to Django!")
    print("[MIGRATION NOTICE] Starting Django server via manage.py runserver...")
    print("=" * 60)
    import subprocess
    subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:5000"])
