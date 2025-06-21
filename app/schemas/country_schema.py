from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Country

class CountrySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Country
        load_instance = True
        include_fk = True
