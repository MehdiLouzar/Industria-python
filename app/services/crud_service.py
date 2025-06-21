from typing import Any, Tuple
from flask import abort

from .. import db


class CRUDService:
    """Generic service for basic CRUD operations."""

    def __init__(self, model):
        self.model = model

    def list(self):
        return self.model.query.all()

    def get_or_404(self, pk: Any):
        obj = self.model.query.get(pk)
        if obj is None:
            abort(404)
        return obj

    def create(self, obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    def update(self, obj):
        db.session.commit()
        return obj

    def delete(self, obj):
        db.session.delete(obj)
        db.session.commit()
