from marshmallow import fields, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from ..models import Zone
from ..utils import point_from_lambert, lambert_from_point

class ZoneSchema(SQLAlchemyAutoSchema):
    # Conversion du total_area (Numeric) en float
    total_area = fields.Float()

    # Sérialisation de la géométrie héritée (SpatialEntity.geometry)
    geometry = fields.Method("get_geometry", dump_only=True)
    # Sérialisation du centroïde
    centroid = fields.Method("get_centroid", dump_only=True)
    lambert_x = fields.Method("get_lambert_x", dump_only=True, allow_none=True)
    lambert_y = fields.Method("get_lambert_y", dump_only=True, allow_none=True)
    lambert_x_input = fields.Float(load_only=True, data_key="lambert_x")
    lambert_y_input = fields.Float(load_only=True, data_key="lambert_y")

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

    @pre_load
    def convert_lambert(self, data, **kwargs):
        x = data.pop("lambert_x", None)
        y = data.pop("lambert_y", None)
        if x is not None and y is not None:
            data["geometry"] = point_from_lambert(x, y)
        return data

    def get_lambert_x(self, obj):
        if obj.geometry is None:
            return None
        x, _ = lambert_from_point(to_shape(obj.geometry))
        return x

    def get_lambert_y(self, obj):
        if obj.geometry is None:
            return None
        _, y = lambert_from_point(to_shape(obj.geometry))
        return y
