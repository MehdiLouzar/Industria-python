from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import ARRAY
from .. import db
from .spatial_entity import SpatialEntity

class Parcel(SpatialEntity):
    __tablename__ = 'parcels'
    id = db.Column(db.Integer, db.ForeignKey('spatial_entities.id'), primary_key=True)

    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    area = db.Column(db.Numeric)
    is_free = db.Column(db.Boolean, default=True)
    is_available = db.Column(db.Boolean, default=True)
    is_showroom = db.Column(db.Boolean, default=False)
    CoS = db.Column(db.Numeric)
    CuS = db.Column(db.Numeric)
    photos = db.Column(ARRAY(db.Text))

    __mapper_args__ = {
        'polymorphic_identity': 'parcel'
    }

    zone = db.relationship(
        'Zone', back_populates='parcels', foreign_keys=[zone_id]
    )
    appointments = db.relationship(
        'Appointment', back_populates='parcel', cascade='all, delete-orphan'
    )
    amenities = db.relationship(
        'ParcelAmenity', back_populates='parcel', cascade='all, delete-orphan'
    )
