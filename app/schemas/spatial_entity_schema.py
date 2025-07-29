from marshmallow import fields, pre_load
import re
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from geoalchemy2.shape import to_shape
from app.models.spatial_entity import SpatialEntity
from ..utils import polygon_from_lambert, lambert_from_polygon

class SpatialEntitySchema(SQLAlchemyAutoSchema):
    geometry = fields.Method("get_geometry", deserialize="pass_through")
    lambert_coords = fields.Method(
        "get_lambert_coords", dump_only=True, allow_none=True
    )

    class Meta:
        model = SpatialEntity
        load_instance = True
        include_fk = True
        exclude = ()  # n'exclut rien, sauf si besoin

    def get_geometry(self, obj):
        return obj.geometry_geojson

    @pre_load
    def convert_lambert(self, data, **kwargs):
        coords = data.pop("lambert_coords", None)
        if isinstance(coords, str):
            parts = re.split(r"[\n;]+", coords)
            coords = [
                [float(n) for n in re.split(r"[,\s]+", p.strip()) if n]
                for p in parts
                if p.strip()
            ]
        if coords:
            geom = polygon_from_lambert(coords)
            if geom is not None:
                data["geometry"] = geom
        return data

    def pass_through(self, value):
        return value

    def get_lambert_coords(self, obj):
        return obj.lambert_coords
