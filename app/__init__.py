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
        # === S'ASSURER QUE POSTGIS EST DISPONIBLE ===
        try:
            # Vérifier si PostGIS est installé
            result = db.session.execute(text("SELECT extname FROM pg_extension WHERE extname = 'postgis';"))
            if result.scalar():
                logging.info("✅ PostGIS extension is available")
            else:
                logging.warning("⚠️ PostGIS extension not found, trying to create...")
                db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                db.session.commit()
                logging.info("✅ PostGIS extension created")
        except Exception as e:
            logging.warning(f"⚠️ PostGIS check failed: {e}")
        
        # === IMPORTER LES MODÈLES ===
        from . import models
        
        # === CRÉER LES TABLES (Model First) ===
        try:
            # Vérifier si les tables existent déjà
            existing_tables = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)).fetchall()
            
            table_names = [row[0] for row in existing_tables]
            
            if not table_names:
                logging.info("🔨 No tables found, creating from models...")
                db.create_all()
                logging.info("✅ Database tables created from SQLAlchemy models")
            else:
                logging.info(f"📋 Found existing tables: {', '.join(table_names)}")
                
                # Vérifier si toutes les tables nécessaires existent
                missing_tables = []
                required_tables = ['countries', 'regions', 'zones', 'activities', 'amenities']
                
                for table in required_tables:
                    if table not in table_names:
                        missing_tables.append(table)
                
                if missing_tables:
                    logging.info(f"🔨 Creating missing tables: {', '.join(missing_tables)}")
                    db.create_all()
                    logging.info("✅ Missing tables created")
                else:
                    logging.info("✅ All required tables exist")
                    
        except Exception as e:
            logging.error(f"❌ Table creation/verification failed: {e}")
            raise

        # === VÉRIFIER LA POPULATION DES DONNÉES ===
        try:
            # Vérifier si des données de base existent
            country_count = db.session.execute(text("SELECT COUNT(*) FROM countries")).scalar()
            region_count = db.session.execute(text("SELECT COUNT(*) FROM regions")).scalar()
            
            if country_count == 0 or region_count == 0:
                logging.info("📊 No demo data found - will be populated by SQL script")
            else:
                logging.info(f"📊 Demo data exists: {country_count} countries, {region_count} regions")
                
        except Exception as e:
            logging.warning(f"⚠️ Could not check demo data: {e}")
    
    # === ENREGISTREMENT DES ROUTES ===
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Initialiser Flask-Login
    login_manager.init_app(app)
    
    # === INFORMATION DE DÉMARRAGE ===
    is_docker = os.environ.get("DOCKER_ENV") == "true"
    env_info = "🐳 Docker environment" if is_docker else "💻 Local environment"
    
    logging.info(f"🚀 Industria app initialized successfully ({env_info})")
    logging.info("📋 Initialization summary:")
    logging.info("   ✅ Flask app configured")
    logging.info("   ✅ Database connection established")
    logging.info("   ✅ Tables created/verified via SQLAlchemy")
    logging.info("   ✅ Routes registered")
    logging.info("   ✅ Authentication configured")
    
    return app

