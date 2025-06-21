from .. import db

class ZoneActivity(db.Model):
    __tablename__ = 'zone_activities'
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), primary_key=True)

    zone = db.relationship('Zone', back_populates='activities')
    activity = db.relationship('Activity', back_populates='zones')
