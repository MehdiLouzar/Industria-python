from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Role

class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True
        include_fk = True
