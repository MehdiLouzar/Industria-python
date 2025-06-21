from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Parcel

class ParcelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Parcel
        load_instance = True
        include_fk = True
