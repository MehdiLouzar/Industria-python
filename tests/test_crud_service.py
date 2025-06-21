from flask import abort
import pytest
from flask_sqlalchemy import SQLAlchemy

from app.services.crud_service import CRUDService
from app import db

class Example(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

def test_crud_lifecycle(app, session):
    svc = CRUDService(Example)
    obj = Example(name='test')
    svc.create(obj)

    all_items = svc.list()
    assert len(all_items) == 1

    fetched = svc.get_or_404(obj.id)
    assert fetched.name == 'test'

    fetched.name = 'changed'
    svc.update(fetched)
    assert svc.get_or_404(obj.id).name == 'changed'

    svc.delete(fetched)
    assert svc.list() == []


def test_get_or_404_not_found(app):
    svc = CRUDService(Example)
    with pytest.raises(Exception):
        svc.get_or_404(123)
