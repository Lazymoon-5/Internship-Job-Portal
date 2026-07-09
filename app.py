from flask import Flask, jsonify
from flask_cors import CORS

from config.config import Config
from config.database import init_db, is_db_available
from routes.student_routes import student_bp
from routes.client_routes import client_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]}}, supports_credentials=True)

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
        print("=" * 60)

    app.register_blueprint(student_bp)
    app.register_blueprint(client_bp)

    @app.route("/")
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Placify backend is running."
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)