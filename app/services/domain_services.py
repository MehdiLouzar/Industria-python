from flask import abort
from geoalchemy2.shape import to_shape, from_shape

from .crud_service import CRUDService
from ..models import (
    Country,
    Region,
    Zone,
    Parcel,
    User,
    AppointmentStatus,
)


class CountryService(CRUDService):
    def delete(self, obj):
        if obj.regions:
            abort(400, "Cannot delete country with regions")
        super().delete(obj)


class RegionService(CRUDService):
    def create(self, obj):
        if obj.country_id and not Country.query.get(obj.country_id):
            abort(400, "Country not found")
        return super().create(obj)

    def update(self, obj):
        if obj.country_id and not Country.query.get(obj.country_id):
            abort(400, "Country not found")
        return super().update(obj)

    def delete(self, obj):
        if obj.zones:
            abort(400, "Cannot delete region with zones")
        super().delete(obj)


class ZoneService(CRUDService):
    def create(self, obj):
        if obj.region_id and not Region.query.get(obj.region_id):
            abort(400, "Region not found")
        if obj.geometry is not None and obj.centroid is None:
            shp = to_shape(obj.geometry)
            obj.centroid = from_shape(shp.centroid, srid=4326)
        return super().create(obj)

    def update(self, obj):
        if obj.region_id and not Region.query.get(obj.region_id):
            abort(400, "Region not found")
        if obj.geometry is not None:
            shp = to_shape(obj.geometry)
            obj.centroid = from_shape(shp.centroid, srid=4326)
        return super().update(obj)

    def delete(self, obj):
        if obj.parcels:
            abort(400, "Cannot delete zone with parcels")
        super().delete(obj)


class ParcelService(CRUDService):
    def create(self, obj):
        if obj.zone_id and not Zone.query.get(obj.zone_id):
            abort(400, "Zone not found")
        return super().create(obj)

    def update(self, obj):
        if obj.zone_id and not Zone.query.get(obj.zone_id):
            abort(400, "Zone not found")
        return super().update(obj)


class AppointmentService(CRUDService):
    def create(self, obj):
        if obj.user_id and not User.query.get(obj.user_id):
            abort(400, "User not found")
        if obj.parcel_id and not Parcel.query.get(obj.parcel_id):
            abort(400, "Parcel not found")
        if obj.appointment_status_id and not AppointmentStatus.query.get(obj.appointment_status_id):
            abort(400, "Appointment status not found")
        return super().create(obj)

    def update(self, obj):
        if obj.user_id and not User.query.get(obj.user_id):
            abort(400, "User not found")
        if obj.parcel_id and not Parcel.query.get(obj.parcel_id):
            abort(400, "Parcel not found")
        if obj.appointment_status_id and not AppointmentStatus.query.get(obj.appointment_status_id):
            abort(400, "Appointment status not found")
        return super().update(obj)
