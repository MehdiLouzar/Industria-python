from datetime import datetime
from geoalchemy2 import Geometry
from .. import db

class SpatialEntity(db.Model):
    __tablename__ = 'spatial_entities'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    geometry = db.Column(Geometry('GEOMETRY'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_on': entity_type,
        'polymorphic_identity': 'spatial_entity'
    }
