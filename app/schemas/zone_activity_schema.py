from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import ZoneActivity

class ZoneActivitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ZoneActivity
        load_instance = True
        include_fk = True
