from geoalchemy2 import Geometry
from .. import db
from .spatial_entity import SpatialEntity

class Zone(SpatialEntity):
    __tablename__ = 'zones'
    id = db.Column(db.Integer, db.ForeignKey('spatial_entities.id'), primary_key=True)

    zone_type_id = db.Column(db.Integer, db.ForeignKey('zone_types.id'))
    is_available = db.Column(db.Boolean, default=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    total_area = db.Column(db.Numeric)
    total_parcels = db.Column(db.Integer)
    available_parcels = db.Column(db.Integer)
    color = db.Column(db.String)
    centroid = db.Column(Geometry('GEOMETRY'))

    __mapper_args__ = {
        'polymorphic_identity': 'zone'
    }

    region = db.relationship('Region', back_populates='zones')
    parcels = db.relationship(
        'Parcel', back_populates='zone', foreign_keys='Parcel.zone_id',
        cascade='all, delete-orphan'
    )
    activities = db.relationship(
        'ZoneActivity', back_populates='zone', cascade='all, delete-orphan'
    )
    zone_type = db.relationship('ZoneType', back_populates='zones')
