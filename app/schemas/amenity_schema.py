from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Amenity

class AmenitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Amenity
        load_instance = True
        include_fk = True
