from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from ..models import Parcel

class ParcelSchema(SQLAlchemyAutoSchema):
    # Override des Numeric → Float
    area = fields.Float()
    CoS = fields.Float(attribute="CoS")  # ou 'CoS' si c'est bien le nom de l'attribut
    CuS = fields.Float(attribute="CuS")  # pareil pour 'CuS'

    # Géométrie en GeoJSON
    geometry = fields.Method("get_geometry", dump_only=True)

    class Meta:
        model = Parcel
        load_instance = True
        include_fk = True

    def get_geometry(self, obj):
        shapely_geom = to_shape(obj.geometry)
        return shapely_geom.__geo_interface__
