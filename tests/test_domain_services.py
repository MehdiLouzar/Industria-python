import pytest
from app import db
from app.models import Country, Region, Zone, Parcel, User, AppointmentStatus, Appointment
from app.services.domain_services import (
    CountryService, RegionService, ZoneService,
    ParcelService, AppointmentService
)


def test_country_delete_with_regions(app):
    country = Country(name='A', code='A')
    region = Region(name='R', country=country)
    db.session.add_all([country, region])
    db.session.commit()

    svc = CountryService(Country)
    with pytest.raises(Exception):
        svc.delete(country)


def test_region_create_missing_country(app):
    svc = RegionService(Region)
    region = Region(name='R', country_id=999)
    with pytest.raises(Exception):
        svc.create(region)


def test_zone_create_missing_region(app):
    svc = ZoneService(Zone)
    zone = Zone(entity_type='zone', name='Z', region_id=999)
    with pytest.raises(Exception):
        svc.create(zone)


def test_parcel_create_missing_zone(app):
    svc = ParcelService(Parcel)
    parcel = Parcel(entity_type='parcel', name='P', zone_id=999)
    with pytest.raises(Exception):
        svc.create(parcel)


def test_appointment_create_missing_user(app):
    status = AppointmentStatus(status_name='new')
    db.session.add(status)
    db.session.commit()
    svc = AppointmentService(Appointment)
    appt = Appointment(user_id=999, parcel_id=None, appointment_status_id=status.id)
    with pytest.raises(Exception):
        svc.create(appt)
