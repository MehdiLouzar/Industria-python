from .. import db

class ParcelAmenity(db.Model):
    __tablename__ = 'parcel_amenities'
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'), primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenities.id'), primary_key=True)

    parcel = db.relationship('Parcel', back_populates='amenities')
    amenity = db.relationship('Amenity', back_populates='parcels')
