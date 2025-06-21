from datetime import datetime
from .. import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'))
    appointment_status_id = db.Column(db.Integer, db.ForeignKey('appointment_statuses.id'))
    requested_date = db.Column(db.Date)
    confirmed_date = db.Column(db.DateTime)
    appointment_message = db.Column(db.Text)
    contact_phone = db.Column(db.String)
    company_name = db.Column(db.String)
    job_title = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='appointments')
    parcel = db.relationship('Parcel', back_populates='appointments')
    status = db.relationship('AppointmentStatus', back_populates='appointments')
