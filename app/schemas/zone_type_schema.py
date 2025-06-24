from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import ZoneType

class ZoneTypeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ZoneType
        load_instance = True
        include_fk = True

