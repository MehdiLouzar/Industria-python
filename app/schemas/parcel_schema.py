from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Parcel

class ParcelSchema(SQLAlchemyAutoSchema):
    geometry = fields.Method("get_geometry", dump_only=True)

    class Meta:
        model = Parcel
        load_instance = True
        include_fk = True

    def get_geometry(self, obj):
        return obj.geometry_geojson()
