from flask import (
    Blueprint,
    jsonify,
    request,
    abort,
    g,
    render_template,
    session,
    redirect,
    url_for,
    current_app,
)
from werkzeug.utils import secure_filename
import os
from datetime import date
from geoalchemy2.shape import to_shape
from .utils import shapely_to_wgs84
from flask_login import login_user, logout_user, login_required, current_user
from flask_restx import Resource
from . import db
from .services import LoginService, KeycloakAdminService
from .services import (
    CRUDService,
    CountryService,
    RegionService,
    ZoneService,
    ParcelService,
    AppointmentService,
)
from .models import (
    Country,
    Region,
    Amenity,
    Zone,
    ZoneType,
    Activity,
    Parcel,
    ActivityLog,
    AppointmentStatus,
    Appointment,
    ZoneActivity,
    ParcelAmenity,
)
from .schemas import (
    CountrySchema,
    RegionSchema,
    AmenitySchema,
    ZoneSchema,
    ZoneTypeSchema,
    ActivitySchema,
    ParcelSchema,
    ActivityLogSchema,
    AppointmentStatusSchema,
    AppointmentSchema,
    ZoneActivitySchema,
    ParcelAmenitySchema,
)
from .swagger import api
from .auth import SessionUser

bp = Blueprint("main", __name__)
api.init_app(bp)


# Basic OpenAPI specification that will be populated dynamically when routes are
# registered. Only minimal information is provided so that Swagger UI can
# present the available endpoints.
openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": "Industria API", "version": "1.0"},
    "paths": {},
}


@bp.route("/")
def index():
    return render_template("home.html", user=session.get("user"))
    # return jsonify(message='Bonjour, Flask avec Docker !')


@bp.route("/login", methods=["GET"])
def login_form():
    """Render the login page."""
    return render_template("login.html")


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, "Missing credentials")

    svc = LoginService()
    try:
        # Authentification avec Keycloak
        tokens = svc.login(username, password)
        userinfo = svc.userinfo(tokens["access_token"])
        
        print(f"✅ Login successful for: {userinfo.get('preferred_username', username)}")
        print(f"📧 Email: {userinfo.get('email')}")
        print(f"🎭 Roles: {userinfo.get('realm_access', {}).get('roles', [])}")
        
    except Exception as exc:
        print(f"❌ Login failed: {exc}")
        abort(401, description=str(exc))

    session["user"] = userinfo
    user = SessionUser(userinfo)
    login_user(user)

    return jsonify({
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "user": {
            "username": userinfo.get("preferred_username"),
            "email": userinfo.get("email"),
            "name": f"{userinfo.get('given_name', '')} {userinfo.get('family_name', '')}".strip(),
            "roles": userinfo.get('realm_access', {}).get('roles', [])
        }
    })

@bp.route("/logout", methods=["POST"])
def logout():
    # Déconnecte Flask-Login
    logout_user()
    # Nettoie ta session Keycloak
    session.pop("user", None)
    g.pop("token_payload", None)
    # Redirige vers la home
    return redirect(url_for("main.index"))


def register_crud_routes(service: CRUDService, schema, endpoint: str):
    """Register CRUD routes for a model on the given endpoint."""
    single_schema = schema()
    many_schema = schema(many=True)
    ns = api.namespace(
        endpoint, path=f"/{endpoint}", description=f"Operations on {endpoint}"
    )

    payload_model = ns.schema_model(f"{endpoint}_payload", {"type": "object"})

    @ns.route("/")
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

    @ns.route("/<int:item_id>")
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
                obj = schema.load(data, instance=obj, partial=True, session=db.session)
            except Exception as e:
                abort(400, str(e))
            updated = svc.update(obj)
            return schema.dump(updated)

        @login_required
        def delete(self, item_id, svc=service):
            obj = svc.get_or_404(item_id)
            svc.delete(obj)
            return "", 204


# Register CRUD routes for models with simple integer primary keys
register_crud_routes(CountryService(Country), CountrySchema, "countries")
register_crud_routes(RegionService(Region), RegionSchema, "regions")
register_crud_routes(CRUDService(Amenity), AmenitySchema, "amenities")
register_crud_routes(CRUDService(ZoneType), ZoneTypeSchema, "zone_types")
register_crud_routes(ZoneService(Zone), ZoneSchema, "zones")
register_crud_routes(CRUDService(Activity), ActivitySchema, "activities")
register_crud_routes(ParcelService(Parcel), ParcelSchema, "parcels")
register_crud_routes(CRUDService(ActivityLog), ActivityLogSchema, "activity_logs")
register_crud_routes(
    CRUDService(AppointmentStatus), AppointmentStatusSchema, "appointment_statuses"
)
register_crud_routes(AppointmentService(Appointment), AppointmentSchema, "appointments")


# Endpoint to list regions for a given country
@bp.route("/api/countries/<int:country_id>/regions")
@login_required
def regions_by_country(country_id):
    regions = Region.query.filter_by(country_id=country_id).all()
    return RegionSchema(many=True).dump(regions)


# Namespaces for association tables with composite keys
zone_activity_ns = api.namespace(
    "zone_activities", path="/zone_activities", description="Zone/Activity links"
)
zone_activity_payload = zone_activity_ns.schema_model(
    "ZoneActivityPayload", {"type": "object"}
)


@zone_activity_ns.route("/")
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


@zone_activity_ns.route("/<int:zone_id>/<int:activity_id>")
class ZoneActivityResource(Resource):
    @login_required
    def delete(self, zone_id, activity_id):
        svc = CRUDService(ZoneActivity)
        obj = svc.get_or_404((zone_id, activity_id))
        svc.delete(obj)
        return "", 204


parcel_amenity_ns = api.namespace(
    "parcel_amenities", path="/parcel_amenities", description="Parcel/Amenity links"
)
parcel_amenity_payload = parcel_amenity_ns.schema_model(
    "ParcelAmenityPayload", {"type": "object"}
)


@parcel_amenity_ns.route("/")
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


@parcel_amenity_ns.route("/<int:parcel_id>/<int:amenity_id>")
class ParcelAmenityResource(Resource):
    @login_required
    def delete(self, parcel_id, amenity_id):
        svc = CRUDService(ParcelAmenity)
        obj = svc.get_or_404((parcel_id, amenity_id))
        svc.delete(obj)
        return "", 204


# --- File upload endpoints -------------------------------------------------


@bp.route("/api/parcels/<int:parcel_id>/photo", methods=["POST"])
@login_required
def upload_parcel_photo(parcel_id):
    """Upload one or more photos for a parcel."""
    svc = ParcelService(Parcel)
    parcel = svc.get_or_404(parcel_id)
    if "file" not in request.files:
        abort(400, "No file part")
    files = request.files.getlist("file")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    paths = []
    for file in files:
        if file.filename == "":
            continue
        fname = secure_filename(file.filename)
        dest = os.path.join(upload_dir, fname)
        file.save(dest)
        paths.append("uploads/" + fname)
    parcel.photos = (parcel.photos or []) + paths
    db.session.commit()
    return jsonify({"photos": parcel.photos})


@bp.route("/api/amenities/<int:amenity_id>/icon", methods=["POST"])
@login_required
def upload_amenity_icon(amenity_id):
    """Upload icon for an amenity."""
    svc = CRUDService(Amenity)
    amenity = svc.get_or_404(amenity_id)
    if "file" not in request.files:
        abort(400, "No file part")
    file = request.files["file"]
    fname = secure_filename(file.filename)
    dest = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
    file.save(dest)
    amenity.icon = "uploads/" + fname
    db.session.commit()
    return jsonify({"icon": amenity.icon})


@bp.route("/api/activities/<int:activity_id>/icon", methods=["POST"])
@login_required
def upload_activity_icon(activity_id):
    """Upload icon for an activity."""
    svc = CRUDService(Activity)
    activity = svc.get_or_404(activity_id)
    if "file" not in request.files:
        abort(400, "No file part")
    file = request.files["file"]
    fname = secure_filename(file.filename)
    dest = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
    file.save(dest)
    activity.icon = "uploads/" + fname
    db.session.commit()
    return jsonify({"icon": activity.icon})


@bp.route("/manage/<resource>")
@login_required
def manage_resource(resource):
    """Generic HTML page for CRUD management."""
    return render_template("crud.html", resource=resource)


@bp.route("/map/zones")
def zones_geojson():
    """Return zone polygons with centroids as GeoJSON."""
    zones = Zone.query.all()
    features = []
    for z in zones:
        geom = z.geometry or z.centroid
        if geom is None:
            continue
        shp = shapely_to_wgs84(to_shape(geom), getattr(geom, "srid", 4326))
        centroid = None
        if z.centroid is not None:
            cshp = shapely_to_wgs84(
                to_shape(z.centroid), getattr(z.centroid, "srid", 4326)
            )
            centroid = cshp.__geo_interface__
        features.append(
            {
                "type": "Feature",
                "id": z.id,
                "geometry": shp.__geo_interface__,
                "properties": {"name": z.name, "centroid": centroid},
            }
        )
    return jsonify({"type": "FeatureCollection", "features": features})

@bp.route("/map/parcels")
def parcels_geojson():
    """Return parcel geometries as GeoJSON."""
    parcels = Parcel.query.all()
    features = []
    for p in parcels:
        if p.geometry is None:
            continue
        shp = shapely_to_wgs84(to_shape(p.geometry), getattr(p.geometry, "srid", 4326))
        features.append(
            {
                "type": "Feature",
                "id": p.id,
                "geometry": shp.__geo_interface__,
                "properties": {
                    "name": p.name,
                    "zone_id": p.zone_id,
                    "is_free": p.is_free,
                    "is_showroom": p.is_showroom,
                    "area": float(p.area) if p.area is not None else None,
                },
            }
        )
    return jsonify({"type": "FeatureCollection", "features": features})

@bp.route("/map/zones/<int:zone_id>")
def zone_full_geojson(zone_id):
    """Return geometry, parcels and details for a zone."""
    zone = Zone.query.get_or_404(zone_id)
    zone_geom = None
    if zone.geometry is not None:
        shp = shapely_to_wgs84(
            to_shape(zone.geometry), getattr(zone.geometry, "srid", 4326)
        )
        zone_geom = shp.__geo_interface__
    parcels = []
    for p in zone.parcels:
        if p.geometry is None:
            continue
        shp = shapely_to_wgs84(to_shape(p.geometry), getattr(p.geometry, "srid", 4326))
        parcels.append(
            {
                "type": "Feature",
                "id": p.id,
                "geometry": shp.__geo_interface__,
                "properties": {
                    "name": p.name,
                    "is_free": p.is_free,
                    "is_showroom": p.is_showroom,
                    "area": float(p.area) if p.area is not None else None,
                    "CoS": float(p.CoS) if p.CoS is not None else None,
                    "CuS": float(p.CuS) if p.CuS is not None else None,
                },
            }
        )
    activities = [za.activity.label for za in zone.activities]
    return jsonify(
        {
            "id": zone.id,
            "name": zone.name,
            "description": zone.description,
            "available_parcels": zone.available_parcels,
            "color": zone.color,
            "activities": activities,
            "is_available": zone.is_available,
            "geometry": zone_geom,
            "parcels": {"type": "FeatureCollection", "features": parcels},
        }
    )


@bp.route("/zones/<int:zone_id>")
def zone_page(zone_id):
    """Display a map focused on a single zone."""
    zone = Zone.query.get_or_404(zone_id)
    return render_template("zone_detail.html", zone=zone)


@bp.route("/parcels/<int:parcel_id>")
def parcel_page(parcel_id):
    """Display parcel details if it belongs to an available zone."""
    parcel = Parcel.query.get_or_404(parcel_id)
    if not parcel.zone or not parcel.zone.is_available or not parcel.is_free:
        abort(404)
    return render_template("parcel_detail.html", parcel=parcel)


@bp.route("/parcels/<int:parcel_id>/reserve", methods=["GET", "POST"])
def reserve_parcel(parcel_id):
    """Simple reservation form for a parcel."""
    parcel = Parcel.query.get_or_404(parcel_id)
    if not parcel.zone or not parcel.zone.is_available or not parcel.is_free:
        abort(404)

    if request.method == "POST":
        status = AppointmentStatus.query.filter_by(status_name="Pending").first()
        appt = Appointment(
            parcel_id=parcel.id,
            appointment_status_id=status.id if status else None,
            requested_date=date.today(),
            appointment_message=request.form.get("message"),
            contact_phone=request.form.get("phone"),
            company_name=request.form.get("company"),
            job_title=request.form.get("title"),
        )
        db.session.add(appt)
        db.session.commit()
        return redirect(url_for("main.parcel_page", parcel_id=parcel.id))

    return render_template("reserve.html", parcel=parcel)
