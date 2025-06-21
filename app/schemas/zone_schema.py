from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Zone

class ZoneSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Zone
        load_instance = True
        include_fk = True
