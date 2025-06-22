import os
import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
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
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    default_db = "postgresql://postgres:postgres@db:5432/industria"
    database_uri = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Context processor : injecte `user` dans tous les templates
    @app.context_processor
    def inject_user():
        return {"user": session.get("user")}

    # Demande loader: restaure current_user à partir de session['user']
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
        db.create_all()

    login_manager.init_app(app)
    return app
