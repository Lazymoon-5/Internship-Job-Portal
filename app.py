from flask import Flask, jsonify
from flask_cors import CORS

from config.config import Config
from config.database import init_db
from routes.student_routes import student_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow requests from the React frontend during development.
    # Update origins to your actual deployed frontend URL later.
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]}}, supports_credentials=True)

    # Create tables if DB is configured/reachable — otherwise falls back
    # to in-memory storage automatically (see config/database.py)
    from config.database import is_db_available
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
        print("[MODE] Fill in DB_HOST/DB_USER/DB_PASSWORD/DB_NAME in .env")
        print("[MODE] to switch to real MySQL — no code changes needed.")
        print("=" * 60)

    # Register blueprints
    app.register_blueprint(student_bp)

    @app.route("/")
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "CampusBridge backend is running."
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)
