from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Region

class RegionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Region
        load_instance = True
        include_fk = True
