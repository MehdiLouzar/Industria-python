from .. import db

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    activities_key = db.Column(db.String, unique=True)
    label = db.Column(db.String)
    icon = db.Column(db.Text)

    zones = db.relationship(
        'ZoneActivity', back_populates='activity', cascade='all, delete-orphan'
    )
