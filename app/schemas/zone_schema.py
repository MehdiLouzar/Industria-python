from marshmallow import fields
from geoalchemy2.shape import to_shape
from ..models import Zone
from .spatial_entity_schema import SpatialEntitySchema

class ZoneSchema(SpatialEntitySchema):
    id = fields.Int(dump_only=True)
    entity_type = fields.Str(dump_only=True)
    # Conversion du total_area (Numeric) en float
    total_area = fields.Float()

    # Sérialisation de la géométrie héritée (SpatialEntity.geometry)
    # Sérialisation du centroïde
    centroid = fields.Method("get_centroid", dump_only=True)

    class Meta:
        model = Zone
        load_instance = True
        include_fk = True

    def get_centroid(self, obj):
        if obj.centroid is None:
            return None
        shapely_centroid = to_shape(obj.centroid)
        return shapely_centroid.__geo_interface__

