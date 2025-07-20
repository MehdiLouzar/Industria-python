from .. import db

class AppointmentStatus(db.Model):
    __tablename__ = 'appointment_status'

    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String)

    appointments = db.relationship('Appointment', back_populates='status')
