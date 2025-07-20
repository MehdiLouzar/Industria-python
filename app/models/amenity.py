from .. import db

class Amenity(db.Model):
    __tablename__ = 'amenities'

    id = db.Column(db.Integer, primary_key=True)
    amenities_key = db.Column(db.String, unique=True)
    label = db.Column(db.String)
    icon = db.Column(db.Text)

    parcels = db.relationship(
        'ParcelAmenity', back_populates='amenity', cascade='all, delete-orphan'
    )
