from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Zone

class ZoneSchema(SQLAlchemyAutoSchema):
    centroid = fields.Raw()
    geometry = fields.Raw()
    class Meta:
        model = Zone
        load_instance = True
        include_fk = True
