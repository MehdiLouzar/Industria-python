from pyproj import Transformer
from shapely.geometry import Point
from shapely.ops import transform
from geoalchemy2.shape import from_shape

# global transformer from Lambert 93 (EPSG:2154) to WGS84 (EPSG:4326)
_to_wgs84 = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
_to_lambert = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)

def point_from_lambert(x, y):
    """Return a GeoAlchemy geometry from Lambert-93 coordinates."""
    lon, lat = _to_wgs84.transform(x, y)
    pt = Point(lon, lat)
    return from_shape(pt, srid=4326)

def lambert_from_point(pt):
    """Return (x, y) Lambert-93 coordinates from a Shapely geometry."""
    if not hasattr(pt, "x") or not hasattr(pt, "y"):
        pt = pt.centroid
    x, y = _to_lambert.transform(pt.x, pt.y)
    return x, y


def shapely_to_wgs84(geom, srid):
    """Return a geometry transformed to WGS84 if needed."""
    if srid in (4326, None):
        return geom
    transformer = Transformer.from_crs(f"EPSG:{srid}", "EPSG:4326", always_xy=True)
    return transform(transformer.transform, geom)
