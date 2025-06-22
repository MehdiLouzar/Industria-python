from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from ..models import Zone

class ZoneSchema(SQLAlchemyAutoSchema):
    # Conversion du total_area (Numeric) en float
    total_area = fields.Float()

    # Sérialisation de la géométrie héritée (SpatialEntity.geometry)
    geometry = fields.Method("get_geometry", dump_only=True)
    # Sérialisation du centroïde
    centroid = fields.Method("get_centroid", dump_only=True)

    class Meta:
        model = Zone
        load_instance = True
        include_fk = True

    def get_geometry(self, obj):
        # to_shape renvoie un objet Shapely
        shapely_geom = to_shape(obj.geometry)
        return shapely_geom.__geo_interface__

    def get_centroid(self, obj):
        shapely_centroid = to_shape(obj.centroid)
        return shapely_centroid.__geo_interface__
