import os
import pytest
from app import create_app, db

@pytest.fixture
def app():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    application = create_app()
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    return db.session
