from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Parcel

class ParcelSchema(SQLAlchemyAutoSchema):
    geometry = fields.Raw()
    class Meta:
        model = Parcel
        load_instance = True
        include_fk = True
