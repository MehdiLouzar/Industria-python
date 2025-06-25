import pytest
from app import db
from app.models import Country, Region, Zone, Parcel, AppointmentStatus, Appointment
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


def test_parcel_in_unavailable_zone_not_free(app):
    region = Region(name='R')
    zone = Zone(entity_type='zone', name='Z', region=region, is_available=False)
    db.session.add_all([region, zone])
    db.session.commit()

    svc = ParcelService(Parcel)
    parcel = Parcel(entity_type='parcel', name='P', zone_id=zone.id, is_free=True)
    svc.create(parcel)

    assert parcel.is_free is False


def test_zone_update_unavailable_sets_parcels_not_free(app):
    region = Region(name='R')
    zone = Zone(entity_type='zone', name='Z', region=region, is_available=True)
    parcel = Parcel(entity_type='parcel', name='P', zone=zone, is_free=True)
    db.session.add_all([region, zone, parcel])
    db.session.commit()

    svc = ZoneService(Zone)
    zone.is_available = False
    svc.update(zone)

    assert parcel.is_free is False

