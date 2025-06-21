from flask import Blueprint, jsonify, request, abort
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

@bp.route('/')
def index():
    return jsonify(message='Bonjour, Flask avec Docker !')


def register_crud_routes(service: CRUDService, schema, endpoint):
    single_schema = schema()
    many_schema = schema(many=True)

    list_url = f'/{endpoint}'
    detail_url = f'/{endpoint}/<int:item_id>'

    @bp.get(list_url)
    @login_required
    def list_items(svc=service, schema=many_schema):
        items = svc.list()
        return jsonify(schema.dump(items))

    @bp.post(list_url)
    @login_required
    def create_item(svc=service, schema=single_schema):
        data = request.get_json() or {}
        try:
            obj = schema.load(data, session=db.session)
        except Exception as e:
            abort(400, str(e))
        obj = svc.create(obj)
        return jsonify(single_schema.dump(obj)), 201

    @bp.get(detail_url)
    @login_required
    def get_item(item_id, svc=service, schema=single_schema):
        obj = svc.get_or_404(item_id)
        return jsonify(schema.dump(obj))

    @bp.put(detail_url)
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

    @bp.delete(detail_url)
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


@bp.get('/parcel_amenities')
@login_required
def list_parcel_amenities():
    svc = CRUDService(ParcelAmenity)
    items = svc.list()
    return jsonify(ParcelAmenitySchema(many=True).dump(items))

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

