
from flask import Blueprint, jsonify, request, abort, render_template_string
from . import db
from .services import CRUDService, CountryService, RegionService, ZoneService, ParcelService, AppointmentService
from .decorators import login_required
from .models import (
    Country, Region, Role, User, Amenity, Zone,
    Activity, Parcel, ActivityLog, AppointmentStatus,
    Appointment, ZoneActivity, ParcelAmenity
)
from .schemas import (
    CountrySchema, RegionSchema, RoleSchema, UserSchema, AmenitySchema,
    ZoneSchema, ActivitySchema, ParcelSchema, ActivityLogSchema,
    AppointmentStatusSchema, AppointmentSchema, ZoneActivitySchema,
    ParcelAmenitySchema
)

bp = Blueprint('main', __name__)

# Basic OpenAPI specification that will be populated dynamically when routes are
# registered. Only minimal information is provided so that Swagger UI can
# present the available endpoints.
openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": "Industria API", "version": "1.0"},
    "paths": {}
}

@bp.route('/')
def index():
    return jsonify(message='Bonjour, Flask avec Docker !')


@bp.get('/openapi.json')
def get_openapi_spec():
    """Return the generated OpenAPI specification as JSON."""
    return jsonify(openapi_spec)


@bp.get('/docs')
def swagger_ui():
    """Serve a minimal Swagger UI for visualising the API."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Swagger UI</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        SwaggerUIBundle({
          url: '/openapi.json',
          dom_id: '#swagger-ui'
        });
      </script>
    </body>
    </html>
    """
    return render_template_string(html)


def register_crud_routes(service: CRUDService, schema, endpoint):
    single_schema = schema()
    many_schema = schema(many=True)

    list_url = f'/{endpoint}'
    detail_url = f'/{endpoint}/<int:item_id>'

    # Populate the OpenAPI specification for these CRUD endpoints
    openapi_spec["paths"].setdefault(list_url, {}).update({
        "get": {
            "summary": f"List {endpoint}",
            "responses": {"200": {"description": "List of objects"}}
        },
        "post": {
            "summary": f"Create {endpoint}",
            "responses": {"201": {"description": "Created"}, "400": {"description": "Validation error"}}
        }
    })
    openapi_spec["paths"].setdefault(detail_url.replace('<int:item_id>', '{item_id}'), {}).update({
        "get": {
            "summary": f"Retrieve {endpoint}",
            "responses": {"200": {"description": "Object details"}, "404": {"description": "Not found"}}
        },
        "put": {
            "summary": f"Update {endpoint}",
            "responses": {"200": {"description": "Updated"}, "400": {"description": "Validation error"}}
        },
        "delete": {
            "summary": f"Delete {endpoint}",
            "responses": {"204": {"description": "Deleted"}}
        }
    })

    @bp.get(list_url, endpoint=f'list_{endpoint}')
    @login_required
    def list_items(svc=service, schema=many_schema):
        items = svc.list()
        return jsonify(schema.dump(items))

    @bp.post(list_url, endpoint=f'create_{endpoint}')
    @login_required
    def create_item(svc=service, schema=single_schema):
        data = request.get_json() or {}
        try:
            obj = schema.load(data, session=db.session)
        except Exception as e:
            abort(400, str(e))
        obj = svc.create(obj)
        return jsonify(single_schema.dump(obj)), 201

    @bp.get(detail_url, endpoint=f'get_{endpoint}')
    @login_required
    def get_item(item_id, svc=service, schema=single_schema):
        obj = svc.get_or_404(item_id)
        return jsonify(schema.dump(obj))

    @bp.put(detail_url, endpoint=f'update_{endpoint}')
    @login_required
    def update_item(item_id, svc=service, schema=single_schema):
        obj = svc.get_or_404(item_id)
        data = request.get_json() or {}
        try:
            obj = schema.load(data, instance=obj, partial=True, session=db.session)
        except Exception as e:
            abort(400, str(e))
        obj = svc.update(obj)
        return jsonify(schema.dump(obj))

    @bp.delete(detail_url, endpoint=f'delete_{endpoint}')
    @login_required
    def delete_item(item_id, svc=service):
        obj = svc.get_or_404(item_id)
        svc.delete(obj)
        return '', 204


# Register CRUD routes for models with simple integer primary keys
register_crud_routes(CountryService(Country), CountrySchema, 'countries')
register_crud_routes(RegionService(Region), RegionSchema, 'regions')
register_crud_routes(CRUDService(Role), RoleSchema, 'roles')
register_crud_routes(CRUDService(User), UserSchema, 'users')
register_crud_routes(CRUDService(Amenity), AmenitySchema, 'amenities')
register_crud_routes(ZoneService(Zone), ZoneSchema, 'zones')
register_crud_routes(CRUDService(Activity), ActivitySchema, 'activities')
register_crud_routes(ParcelService(Parcel), ParcelSchema, 'parcels')
register_crud_routes(CRUDService(ActivityLog), ActivityLogSchema, 'activity_logs')
register_crud_routes(CRUDService(AppointmentStatus), AppointmentStatusSchema, 'appointment_statuses')
register_crud_routes(AppointmentService(Appointment), AppointmentSchema, 'appointments')


# Custom routes for association tables with composite keys
@bp.get('/zone_activities')
@login_required
def list_zone_activities():
    svc = CRUDService(ZoneActivity)
    items = svc.list()
    return jsonify(ZoneActivitySchema(many=True).dump(items))

openapi_spec["paths"].setdefault("/zone_activities", {}).update({
    "get": {
        "summary": "List zone activities",
        "responses": {"200": {"description": "List of zone/activity links"}}
    },
    "post": {
        "summary": "Create zone activity",
        "responses": {"201": {"description": "Created"}, "400": {"description": "Validation error"}}
    }
})

@bp.post('/zone_activities')
@login_required
def create_zone_activity():
    svc = CRUDService(ZoneActivity)
    data = request.get_json() or {}
    try:
        obj = ZoneActivitySchema().load(data, session=db.session)
    except Exception as e:
        abort(400, str(e))
    obj = svc.create(obj)
    return jsonify(ZoneActivitySchema().dump(obj)), 201

@bp.delete('/zone_activities/<int:zone_id>/<int:activity_id>')
@login_required
def delete_zone_activity(zone_id, activity_id):
    svc = CRUDService(ZoneActivity)
    obj = svc.get_or_404((zone_id, activity_id))
    svc.delete(obj)
    return '', 204

openapi_spec["paths"].setdefault("/zone_activities/{zone_id}/{activity_id}", {}).update({
    "delete": {
        "summary": "Delete zone activity",
        "responses": {"204": {"description": "Deleted"}, "404": {"description": "Not found"}}
    }
})


@bp.get('/parcel_amenities')
@login_required
def list_parcel_amenities():
    svc = CRUDService(ParcelAmenity)
    items = svc.list()
    return jsonify(ParcelAmenitySchema(many=True).dump(items))

openapi_spec["paths"].setdefault("/parcel_amenities", {}).update({
    "get": {
        "summary": "List parcel amenities",
        "responses": {"200": {"description": "List of parcel/amenity links"}}
    },
    "post": {
        "summary": "Create parcel amenity",
        "responses": {"201": {"description": "Created"}, "400": {"description": "Validation error"}}
    }
})

@bp.post('/parcel_amenities')
@login_required
def create_parcel_amenity():
    svc = CRUDService(ParcelAmenity)
    data = request.get_json() or {}
    try:
        obj = ParcelAmenitySchema().load(data, session=db.session)
    except Exception as e:
        abort(400, str(e))
    obj = svc.create(obj)
    return jsonify(ParcelAmenitySchema().dump(obj)), 201

@bp.delete('/parcel_amenities/<int:parcel_id>/<int:amenity_id>')
@login_required
def delete_parcel_amenity(parcel_id, amenity_id):
    svc = CRUDService(ParcelAmenity)
    obj = svc.get_or_404((parcel_id, amenity_id))
    svc.delete(obj)
    return '', 204

openapi_spec["paths"].setdefault("/parcel_amenities/{parcel_id}/{amenity_id}", {}).update({
    "delete": {
        "summary": "Delete parcel amenity",
        "responses": {"204": {"description": "Deleted"}, "404": {"description": "Not found"}}
    }
})
