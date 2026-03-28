"""
Robotics Lab Inventory & Usage Management System
Flask Application Entry Point
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from routes.auth      import auth_bp
from routes.items     import items_bp
from routes.usage     import usage_bp
from routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    app.config.from_object(Config)

    # Allow cookies to be sent cross-origin (frontend ↔ backend on same machine)
    CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:3000",
                                                    "http://localhost:5500", "http://127.0.0.1:5500",
                                                    "null"])   # "null" covers file:// origin

    # Register blueprints
    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(items_bp,     url_prefix="/api")
    app.register_blueprint(usage_bp,     url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")

    # Serve frontend files
    @app.route("/")
    def serve_index():
        return send_from_directory(app.static_folder, "login.html")

    @app.route("/<path:filename>")
    def serve_files(filename):
        return send_from_directory(app.static_folder, filename)

    @app.after_request
    def add_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)