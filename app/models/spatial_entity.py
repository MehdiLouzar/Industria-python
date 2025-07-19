from datetime import datetime
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import json

from ..utils import polygon_from_lambert, lambert_from_polygon

from .. import db

class SpatialEntity(db.Model):
    __tablename__ = 'spatial_entities'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    geometry = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326))

    _lambert_cache = None

    __mapper_args__ = {
        'polymorphic_on': entity_type,
        'polymorphic_identity': 'spatial_entity',
    }

    @property
    def geometry_geojson(self):
        """Return geometry as GeoJSON for map rendering."""
        if self.geometry:
            shapely_geom = to_shape(self.geometry)
            return shapely_geom.__geo_interface__
        return None

    @property
    def lambert_coords(self):
        """List of Lambert coordinate pairs used to build the geometry."""
        if self.geometry is not None:
            return lambert_from_polygon(to_shape(self.geometry))
        return self._lambert_cache

    @lambert_coords.setter
    def lambert_coords(self, coords):
        self._lambert_cache = coords
        if coords:
            geom = polygon_from_lambert(coords)
            if geom is not None:
                self.geometry = geom
