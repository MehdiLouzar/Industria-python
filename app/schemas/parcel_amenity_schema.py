from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import ParcelAmenity

class ParcelAmenitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParcelAmenity
        load_instance = True
        include_fk = True
