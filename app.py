from flask import Flask, jsonify
from flask_cors import CORS

from config.config import Config
from routes.student_routes import student_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow requests from the React frontend during development
    CORS(app)

    # Register blueprints
    app.register_blueprint(student_bp)

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
