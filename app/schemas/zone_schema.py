from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Zone

class ZoneSchema(SQLAlchemyAutoSchema):
    geometry = fields.Method("get_geometry", dump_only=True)
    centroid = fields.Method("get_centroid", dump_only=True)

    class Meta:
        model = Zone
        load_instance = True
        include_fk = True

    def get_geometry(self, obj):
        return obj.geometry_geojson()

    def get_centroid(self, obj):
        if obj.centroid:
            from geoalchemy2.shape import to_shape
            return to_shape(obj.centroid).__geo_interface__
        return None
