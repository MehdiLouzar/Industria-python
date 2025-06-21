from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.spatial_entity import SpatialEntity  # ajuste le chemin si besoin

class SpatialEntitySchema(SQLAlchemyAutoSchema):
    geometry = fields.Method("get_geometry", dump_only=True)

    class Meta:
        model = SpatialEntity
        load_instance = True
        include_fk = True
        exclude = ()  # n'exclut rien, sauf si besoin

    def get_geometry(self, obj):
        return obj.geometry_geojson()
