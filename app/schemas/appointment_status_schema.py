from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import AppointmentStatus

class AppointmentStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AppointmentStatus
        load_instance = True
        include_fk = True
