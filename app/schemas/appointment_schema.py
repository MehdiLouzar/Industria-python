from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Appointment

class AppointmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Appointment
        load_instance = True
        include_fk = True
