from marshmallow import fields, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from ..models import Parcel
from ..utils import point_from_lambert, lambert_from_point

class ParcelSchema(SQLAlchemyAutoSchema):
    # Override des Numeric → Float
    area = fields.Float()
    CoS = fields.Float(attribute="CoS")  # ou 'CoS' si c'est bien le nom de l'attribut
    CuS = fields.Float(attribute="CuS")  # pareil pour 'CuS'

    # Géométrie en GeoJSON
    geometry = fields.Method("get_geometry", dump_only=True)
    lambert_x = fields.Method("get_lambert_x", dump_only=True, allow_none=True)
    lambert_y = fields.Method("get_lambert_y", dump_only=True, allow_none=True)
    lambert_x_input = fields.Float(load_only=True, data_key="lambert_x")
    lambert_y_input = fields.Float(load_only=True, data_key="lambert_y")

    class Meta:
        model = Parcel
        load_instance = True
        include_fk = True

    def get_geometry(self, obj):
        shapely_geom = to_shape(obj.geometry)
        return shapely_geom.__geo_interface__

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
