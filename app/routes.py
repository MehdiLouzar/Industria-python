from flask import Blueprint, jsonify, request, abort, g, render_template, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_restx import Resource
from . import db
from .decorators import login_required
from .services import LoginService, KeycloakAdminService
from .services import (
    CRUDService, CountryService, RegionService, ZoneService, ParcelService,
    AppointmentService
)
from .models import (
    Country, Region, Role, User, Amenity, Zone, Activity, Parcel, ActivityLog,
    AppointmentStatus, Appointment, ZoneActivity, ParcelAmenity
)
from .schemas import (
    CountrySchema, RegionSchema, RoleSchema, UserSchema, AmenitySchema,
    ZoneSchema, ActivitySchema, ParcelSchema, ActivityLogSchema,
    AppointmentStatusSchema, AppointmentSchema, ZoneActivitySchema,
    ParcelAmenitySchema
)
from .swagger import api
from .auth import SessionUser

bp = Blueprint('main', __name__)
api.init_app(bp)


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
    return render_template('home.html', user=session.get('user'))
    #return jsonify(message='Bonjour, Flask avec Docker !')


@bp.route('/login', methods=['GET'])
def login_form():
    """Render the login page."""
    return render_template('login.html')


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        abort(400, "Missing credentials")

    svc = LoginService()
    try:
        tokens = svc.login(username, password)
        # récupère les infos utilisateur (sub, preferred_username, email, etc.)
        userinfo = svc.userinfo(tokens["access_token"])
    except Exception as exc:
        abort(401, description=str(exc))

    # stocke le profile dans la session
    session["user"] = userinfo

    # crée l’utilisateur pour Flask-Login et connecte-le
    user = SessionUser(userinfo)
    login_user(user)

    return jsonify(tokens)


@bp.route('/register', methods=['POST'])
def register():
    """Create a user in Keycloak and link it in the local database."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first = data.get('first_name')
    last = data.get('last_name')
    if not username or not password or not email:
        abort(400, 'Missing credentials')
    svc = KeycloakAdminService()
    try:
        kc_id = svc.create_user(username, email, first, last, password)
    except Exception as exc:  # pragma: no cover - pass through errors
        abort(400, description=str(exc))
    user = User(
        first_name=first,
        last_name=last,
        email=email,
        provider='keycloak',
        provider_id=kc_id,
    )
    db.session.add(user)
    db.session.commit()
    return UserSchema().dump(user), 201

@bp.route('/logout', methods=['POST'])
def logout():
    # Déconnecte Flask-Login
    logout_user()
    # Nettoie ta session Keycloak
    session.pop('user', None)
    g.pop('token_payload', None)
    # Redirige vers la home
    return redirect(url_for('main.index'))


def register_crud_routes(service: CRUDService, schema, endpoint: str):
    """Register CRUD routes for a model on the given endpoint."""
    single_schema = schema()
    many_schema = schema(many=True)
    ns = api.namespace(endpoint, path=f'/{endpoint}',
                       description=f'Operations on {endpoint}')

    payload_model = ns.schema_model(f'{endpoint}_payload', {'type': 'object'})

    @ns.route('/')
    class ListResource(Resource):
        @login_required
        def get(self, svc=service, schema=many_schema):
            items = svc.list()
            return schema.dump(items)

        @login_required
        @ns.expect(payload_model)
        def post(self, svc=service, schema=single_schema):
            data = request.get_json() or {}
            try:
                obj = schema.load(data, session=db.session)
            except Exception as e:
                abort(400, str(e))
            created = svc.create(obj)
            return schema.dump(created), 201

    @ns.route('/<int:item_id>')
    class DetailResource(Resource):
        @login_required
        def get(self, item_id, svc=service, schema=single_schema):
            obj = svc.get_or_404(item_id)
            return schema.dump(obj)

        @login_required
        @ns.expect(payload_model)
        def put(self, item_id, svc=service, schema=single_schema):
            obj = svc.get_or_404(item_id)
            data = request.get_json() or {}
            try:
                obj = schema.load(data, instance=obj, partial=True,
                                  session=db.session)
            except Exception as e:
                abort(400, str(e))
            updated = svc.update(obj)
            return schema.dump(updated)

        @login_required
        def delete(self, item_id, svc=service):
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



# Namespaces for association tables with composite keys
zone_activity_ns = api.namespace('zone_activities', path='/zone_activities',
                                 description='Zone/Activity links')
zone_activity_payload = zone_activity_ns.schema_model('ZoneActivityPayload', {'type': 'object'})


@zone_activity_ns.route('/')
class ZoneActivityList(Resource):
    @login_required
    def get(self):
        svc = CRUDService(ZoneActivity)
        items = svc.list()
        return ZoneActivitySchema(many=True).dump(items)

    @login_required
    @zone_activity_ns.expect(zone_activity_payload)
    def post(self):
        svc = CRUDService(ZoneActivity)
        data = request.get_json() or {}
        try:
            obj = ZoneActivitySchema().load(data, session=db.session)
        except Exception as e:
            abort(400, str(e))
        created = svc.create(obj)
        return ZoneActivitySchema().dump(created), 201

@zone_activity_ns.route('/<int:zone_id>/<int:activity_id>')
class ZoneActivityResource(Resource):
    @login_required
    def delete(self, zone_id, activity_id):
        svc = CRUDService(ZoneActivity)
        obj = svc.get_or_404((zone_id, activity_id))
        svc.delete(obj)
        return '', 204


parcel_amenity_ns = api.namespace('parcel_amenities', path='/parcel_amenities',
                                  description='Parcel/Amenity links')
parcel_amenity_payload = parcel_amenity_ns.schema_model('ParcelAmenityPayload', {'type': 'object'})


@parcel_amenity_ns.route('/')
class ParcelAmenityList(Resource):
    @login_required
    def get(self):
        svc = CRUDService(ParcelAmenity)
        items = svc.list()
        return ParcelAmenitySchema(many=True).dump(items)

    @login_required
    @parcel_amenity_ns.expect(parcel_amenity_payload)
    def post(self):
        svc = CRUDService(ParcelAmenity)
        data = request.get_json() or {}
        try:
            obj = ParcelAmenitySchema().load(data, session=db.session)
        except Exception as e:
            abort(400, str(e))
        created = svc.create(obj)
        return ParcelAmenitySchema().dump(created), 201

@parcel_amenity_ns.route('/<int:parcel_id>/<int:amenity_id>')
class ParcelAmenityResource(Resource):
    @login_required
    def delete(self, parcel_id, amenity_id):
        svc = CRUDService(ParcelAmenity)
        obj = svc.get_or_404((parcel_id, amenity_id))
        svc.delete(obj)
        return '', 204
