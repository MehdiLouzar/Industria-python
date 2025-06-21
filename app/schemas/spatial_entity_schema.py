from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import SpatialEntity

class SpatialEntitySchema(SQLAlchemyAutoSchema):
    # Geometry columns from GeoAlchemy2 are not automatically supported by
    # marshmallow-sqlalchemy. Represent them as raw strings to avoid
    # conversion errors during schema creation.
    geometry = fields.Raw()
    class Meta:
        model = SpatialEntity
        load_instance = True
        include_fk = True
