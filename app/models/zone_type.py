from .. import db

class ZoneType(db.Model):
    __tablename__ = 'zone_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    zones = db.relationship('Zone', back_populates='zone_type')

