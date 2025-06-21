from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import SpatialEntity

class SpatialEntitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SpatialEntity
        load_instance = True
        include_fk = True
