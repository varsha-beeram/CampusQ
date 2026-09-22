import os
from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, jwt

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///campusq.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "campusq-dev-secret-change-in-production")
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth import bp as auth_bp
    from .routes.catalog import bp as catalog_bp
    from .routes.queue import bp as queue_bp
    from .routes.staff import bp as staff_bp
    from .routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(catalog_bp, url_prefix="/api")
    app.register_blueprint(queue_bp, url_prefix="/api")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/api/health")
    def health():
        return jsonify(success=True, message="CampusQ API is running")

    with app.app_context():
        db.create_all()
    return app
