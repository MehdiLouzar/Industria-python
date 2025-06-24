from datetime import datetime
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import json

from .. import db

class SpatialEntity(db.Model):
    __tablename__ = 'spatial_entities'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    geometry = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326))

    __mapper_args__ = {
        'polymorphic_on': entity_type,
        'polymorphic_identity': 'spatial_entity',
    }

    def geometry_geojson(self):
        """Retourne la géométrie en format GeoJSON pour l'API."""
        if self.geometry:
            shapely_geom = to_shape(self.geometry)
            return shapely_geom.__geo_interface__  # GeoJSON-compatible dict
        return None
