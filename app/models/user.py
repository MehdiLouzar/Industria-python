
from datetime import datetime
from .. import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.Text)
    provider = db.Column(db.String)
    provider_id = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    activation_token = db.Column(db.Text)
    user_role = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role', back_populates='users')
    appointments = db.relationship('Appointment', back_populates='user')
    activity_logs = db.relationship('ActivityLog', back_populates='user')
