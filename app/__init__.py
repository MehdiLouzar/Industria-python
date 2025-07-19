import os
import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from .swagger import api

db = SQLAlchemy()

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = "main.login_form"

def create_app():
    app = Flask(__name__)

    # Configuration de base
    app.secret_key = os.environ.get("SECRET_KEY", "change_me_in_production")

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    )

    # Configuration base de données
    default_db = "postgresql://postgres:postgres@db:5432/industria"
    database_uri = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configuration uploads
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # === RESSOURCES CRUD (SANS users/roles) ===
    CRUD_RESOURCES = [
        "countries",
        "regions", 
        "amenities",
        "zone_types",
        "zones",
        "activities",
        "parcels",
        "activity_logs",
        "appointment_statuses",
        "appointments",
        "zone_activities",
        "parcel_amenities",
    ]

    # Context processor
    @app.context_processor
    def inject_globals():
        return {
            "user": session.get("user"),
            "crud_resources": CRUD_RESOURCES,
        }

    # === CONFIGURATION FLASK-LOGIN POUR KEYCLOAK ===
    from .auth import SessionUser

    @login_manager.request_loader
    def load_user_from_request(request):
        info = session.get("user")
        if not info:
            return None
        return SessionUser(info)

    # === INITIALISATION DB ===
    db.init_app(app)
    
    with app.app_context():
        # === CRÉER LES EXTENSIONS POSTGIS ===
        try:
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            db.session.commit()
            logging.info("✅ PostGIS extension ensured")
        except Exception as e:
            logging.warning(f"⚠️ Could not ensure PostGIS extension: {e}")
        
        # === IMPORTER LES MODÈLES ===
        from . import models
        
        # === CRÉER LES TABLES (Model First) ===
        try:
            db.create_all()
            logging.info("✅ Database tables created from models")
        except Exception as e:
            logging.error(f"❌ Table creation failed: {e}")
            raise

        # === LES DONNÉES SERONT INSÉRÉES PAR LE SCRIPT SQL ===
        logging.info("ℹ️ Tables ready - data will be populated by SQL script")
    
    # === ENREGISTREMENT DES ROUTES ===
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Initialiser Flask-Login
    login_manager.init_app(app)
    
    logging.info("🚀 Industria app initialized successfully")
    return app