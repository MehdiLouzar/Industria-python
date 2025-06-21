from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Activity

class ActivitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Activity
        load_instance = True
        include_fk = True
