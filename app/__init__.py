import os
import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from .swagger import api

db = SQLAlchemy()

from .routes import bp as main_bp

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "main.login_form"


def create_app():
    app = Flask(__name__)

    # Nécessaire pour utiliser session
    app.secret_key = os.environ.get("SECRET_KEY", "change_me")

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    )
    default_db = "postgresql://postgres:postgres@db:5432/industria"
    database_uri = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Folder for uploaded images
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Resources disponibles pour le CRUD generique
    CRUD_RESOURCES = [
        "countries",
        "regions",
        "roles",
        "users",
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

    # Context processor : injecte `user` et la liste des ressources
    @app.context_processor
    def inject_globals():
        return {"user": session.get("user"), "crud_resources": CRUD_RESOURCES}

    from .auth import SessionUser

    @login_manager.request_loader
    def load_user_from_request(request):
        info = session.get("user")
        if not info:
            return None
        return SessionUser(info)

    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        from . import models  # noqa: F401  ensure models are registered

        # Auto-upgrade legacy databases that predate zone_types
        insp = db.inspect(db.engine)
        zone_cols = [c['name'] for c in insp.get_columns('zones')] if 'zones' in insp.get_table_names() else []

        if 'zone_type' in zone_cols and 'zone_type_id' not in zone_cols:
            db.session.execute(text('ALTER TABLE zones RENAME COLUMN zone_type TO zone_type_id'))
        if 'zone_type_id' not in zone_cols and 'zones' in insp.get_table_names():
            db.session.execute(text('ALTER TABLE zones ADD COLUMN zone_type_id INTEGER'))
        if 'zone_description' in zone_cols:
            db.session.execute(text('ALTER TABLE zones DROP COLUMN zone_description'))
        if 'county_code' in zone_cols:
            db.session.execute(text('ALTER TABLE zones DROP COLUMN county_code'))

        if 'zone_types' not in insp.get_table_names():
            db.session.execute(text(
                'CREATE TABLE IF NOT EXISTS zone_types ('
                'id SERIAL PRIMARY KEY, name VARCHAR NOT NULL UNIQUE)'
            ))
        db.session.execute(text(
            "INSERT INTO zone_types (id, name) VALUES (1, 'privée'), (2, 'public') "
            'ON CONFLICT DO NOTHING'
        ))
        db.session.execute(text(
            'ALTER TABLE zones '
            'ADD CONSTRAINT IF NOT EXISTS zones_zone_type_id_fkey '
            'FOREIGN KEY (zone_type_id) REFERENCES zone_types(id)'
        ))
        db.session.commit()

        db.create_all()

    login_manager.init_app(app)
    return app
