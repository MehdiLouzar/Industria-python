from flask import abort
from geoalchemy2.shape import to_shape, from_shape

from .crud_service import CRUDService
from .. import db
from ..models import (
    Country,
    Region,
    Zone,
    Parcel,
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
        if obj.geometry is not None:
            shp = to_shape(obj.geometry)
            obj.centroid = from_shape(shp.centroid, srid=4326)
        created = super().create(obj)
        if created.is_available is False:
            for parcel in created.parcels:
                parcel.is_free = False
            db.session.commit()
        return created

    def update(self, obj):
        if obj.region_id and not Region.query.get(obj.region_id):
            abort(400, "Region not found")
        if obj.geometry is not None:
            shp = to_shape(obj.geometry)
            obj.centroid = from_shape(shp.centroid, srid=4326)
        if obj.is_available is False:
            for parcel in obj.parcels:
                parcel.is_free = False
            db.session.flush()
        return super().update(obj)

    def delete(self, obj):
        """Delete a zone and all linked parcels."""
        super().delete(obj)


class ParcelService(CRUDService):
    def create(self, obj):
        if obj.zone_id and not Zone.query.get(obj.zone_id):
            abort(400, "Zone not found")
        zone = Zone.query.get(obj.zone_id) if obj.zone_id else None
        if zone and zone.is_available is False:
            obj.is_free = False
        return super().create(obj)

    def update(self, obj):
        if obj.zone_id and not Zone.query.get(obj.zone_id):
            abort(400, "Zone not found")
        zone = Zone.query.get(obj.zone_id) if obj.zone_id else None
        if zone and zone.is_available is False:
            obj.is_free = False
        return super().update(obj)


class AppointmentService(CRUDService):
    def create(self, obj):
        if obj.parcel_id and not Parcel.query.get(obj.parcel_id):
            abort(400, "Parcel not found")
        if obj.appointment_status_id and not AppointmentStatus.query.get(obj.appointment_status_id):
            abort(400, "Appointment status not found")
        return super().create(obj)

    def update(self, obj):
        if obj.parcel_id and not Parcel.query.get(obj.parcel_id):
            abort(400, "Parcel not found")
        if obj.appointment_status_id and not AppointmentStatus.query.get(obj.appointment_status_id):
            abort(400, "Appointment status not found")
        return super().update(obj)
    
from ..services.activity_logger import ActivityLogger

class ZoneService(CRUDService):
    def create(self, obj):
        created = super().create(obj)
        # Logger la création
        ActivityLogger.log_zone_created(created)
        return created
    
    def update(self, obj):
        updated = super().update(obj)
        # Logger la modification
        ActivityLogger.log_zone_updated(updated)
        return updated
    
    def delete(self, obj):
        # Logger avant suppression (pour avoir encore les infos)
        ActivityLogger.log_zone_deleted(obj)
        super().delete(obj)

class AppointmentService(CRUDService):
    def create(self, obj):
        created = super().create(obj)
        # Logger la création de RDV
        if created.parcel:
            ActivityLogger.log_parcel_reserved(created.parcel, created)
        return created
