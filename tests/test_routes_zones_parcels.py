import pytest
from unittest.mock import patch, MagicMock


def _fake_shape():
    shape = MagicMock()
    shape.__geo_interface__ = {"type": "Point", "coordinates": [0, 0]}
    return shape


def test_zone_full_geojson(app):
    zone = MagicMock()
    zone.id = 1
    zone.name = "Z1"
    zone.description = "desc"
    zone.available_parcels = 2
    zone.color = "#000"
    zone.is_available = True
    zone.geometry = "g"
    parcel = MagicMock()
    parcel.id = 10
    parcel.geometry = "pg"
    parcel.name = "P1"
    parcel.is_free = True
    parcel.is_showroom = False
    parcel.area = 100
    parcel.CoS = None
    parcel.CuS = None
    zone.parcels = [parcel]
    zone.activities = [MagicMock(activity=MagicMock(label="A"))]

    with patch("app.routes.Zone") as Zone, \
         patch("app.routes.to_shape", side_effect=lambda g: _fake_shape()), \
         patch("app.routes.shapely_to_wgs84", side_effect=lambda geom, srid: geom):
        Zone.query.get_or_404.return_value = zone
        client = app.test_client()
        resp = client.get("/map/zones/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == 1
        assert data["parcels"]["features"][0]["properties"]["name"] == "P1"


def test_zone_page_render(app):
    zone = MagicMock(id=2)
    with patch("app.routes.Zone") as Zone, \
         patch("app.routes.render_template", return_value="OK") as render:
        Zone.query.get_or_404.return_value = zone
        client = app.test_client()
        resp = client.get("/zones/2")
        assert resp.status_code == 200
        assert resp.data == b"OK"
        render.assert_called_once()


def test_parcel_page_404_when_not_free(app):
    zone = MagicMock(is_available=True)
    parcel = MagicMock(zone=zone, is_free=False)
    with patch("app.routes.Parcel") as Parcel:
        Parcel.query.get_or_404.return_value = parcel
        client = app.test_client()
        resp = client.get("/parcels/1")
        assert resp.status_code == 404


def test_parcel_page_ok(app):
    zone = MagicMock(is_available=True)
    parcel = MagicMock(zone=zone, is_free=True)
    with patch("app.routes.Parcel") as Parcel, \
         patch("app.routes.render_template", return_value="OK") as render:
        Parcel.query.get_or_404.return_value = parcel
        client = app.test_client()
        resp = client.get("/parcels/1")
        assert resp.status_code == 200
        assert resp.data == b"OK"
        render.assert_called_once()
