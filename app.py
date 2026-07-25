import os
from flask import Flask, jsonify
from flask_cors import CORS

from config.config import Config
from config.database import init_db, is_db_available
from routes.student_routes import student_bp
from routes.client_routes import client_bp
from routes.admin_routes import admin_bp
from routes.admin_dashboard_routes import admin_dashboard_bp
from routes.admin_students_routes import admin_students_bp
from routes.admin_companies_routes import admin_companies_bp
from routes.admin_jobs_routes import admin_jobs_bp
from routes.admin_applications_routes import admin_applications_bp
from routes.admin_reports_routes import admin_reports_bp
from routes.admin_notifications_routes import admin_notifications_bp
from routes.student_profile_routes import student_profile_bp
from routes.student_resume_routes import student_resume_bp
from routes.student_jobs_routes import student_jobs_bp
from routes.student_applications_routes import student_applications_bp
from routes.client_dashboard_routes import client_dashboard_bp
from routes.client_profile_routes import client_profile_bp
from routes.client_jobs_routes import client_jobs_bp
from routes.client_applicants_routes import client_applicants_bp
from routes.public_jobs_routes import public_jobs_bp
from routes.contact_routes import contact_bp
from routes.client_notifications_routes import client_notifications_bp
from routes.student_notifications_routes import student_notifications_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow requests from the React frontend. Local dev origins are
    # always allowed; add deployed frontend URLs via the ALLOWED_ORIGINS
    # env var (comma-separated) so new frontend domains can be added
    # from Render's dashboard without a code change/redeploy.
    default_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    extra_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
    extra_origins = [o.strip() for o in extra_origins_env.split(",") if o.strip()]
    all_origins = default_origins + extra_origins

    CORS(app, resources={r"/api/*": {"origins": all_origins}}, supports_credentials=True)
    print(f"[CORS] Allowed origins: {all_origins}")

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

    app.register_blueprint(student_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_students_bp)
    app.register_blueprint(admin_companies_bp)
    app.register_blueprint(admin_jobs_bp)
    app.register_blueprint(admin_applications_bp)
    app.register_blueprint(admin_reports_bp)
    app.register_blueprint(admin_notifications_bp)
    app.register_blueprint(student_profile_bp)
    app.register_blueprint(student_resume_bp)
    app.register_blueprint(student_jobs_bp)
    app.register_blueprint(student_applications_bp)
    app.register_blueprint(client_dashboard_bp)
    app.register_blueprint(client_profile_bp)
    app.register_blueprint(client_jobs_bp)
    app.register_blueprint(client_applicants_bp)
    app.register_blueprint(public_jobs_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(client_notifications_bp)
    app.register_blueprint(student_notifications_bp)

    @app.route("/")
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Placify backend is running."
        })

    return app


app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" is required for Render (and most cloud hosts) —
    # binding only to 127.0.0.1 makes the app unreachable from outside
    # the container. Port is read directly from the environment since
    # Render assigns its own PORT value dynamically.
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=port)
