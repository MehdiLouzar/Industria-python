from marshmallow import fields
from ..models import Parcel
from .spatial_entity_schema import SpatialEntitySchema

class ParcelSchema(SpatialEntitySchema):
    id = fields.Int(dump_only=True)
    entity_type = fields.Str(dump_only=True)
    # Override des Numeric → Float
    area = fields.Float()
    CoS = fields.Float(attribute="CoS")
    CuS = fields.Float(attribute="CuS")

    class Meta:
        model = Parcel
        load_instance = True
        include_fk = True

