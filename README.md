# Industria Python

This repository provides a minimal example of how to containerize a Flask application with Docker Compose. It also includes a PostgreSQL database with PostGIS and a Keycloak identity provider.

## Structure

```
./app/                   # Flask application package
    __init__.py         # create_app and blueprint registration
    routes.py           # application routes
    models/             # SQLAlchemy ORM classes
    services/           # external logic services
    decorators.py       # authentication decorators
run.py                  # Entry point for the app
Dockerfile              # Container image for the Flask app
./db/init/initDB.sql    # Script to reset and seed the database
./docker-compose.yml    # Compose configuration
```

## Usage

Build and start the containers:

```bash
docker-compose up --build
```
The Flask application will be available at `http://localhost:8000/`, the PostgreSQL database at `localhost:5432`, and Keycloak at `http://localhost:8080/`.
The application relies entirely on PostgreSQL for persistence.

Database tables are created automatically on first start using SQLAlchemy.
To reset a development database with demo data, run `psql -f db/init/initDB.sql`
once the tables exist. The script truncates all tables and inserts a sample
dataset.

### API documentation

Swagger UI exposing the OpenAPI description of the routes is available once the
containers are running. Navigate to `http://localhost:8000/api/docs` to explore
the API. The raw specification can be fetched at
`http://localhost:8000/api/swagger.json`.

Each documented route includes fields for path parameters and JSON bodies so you
can easily try requests directly from the UI.

### Authentication and registration

The application expects requests to include a JWT access token issued by
Keycloak. Configure the Keycloak realm and client, then set the environment
variables `KEYCLOAK_ISSUER` and `KEYCLOAK_AUDIENCE`.
For logins, the client id used defaults to the value of
`KEYCLOAK_AUDIENCE` but can be overridden via `KEYCLOAK_CLIENT_ID`
if needed (see `docker-compose.yml`).
Routes are protected using these tokens via the provided decorators.

To register a new account, send a POST request to `/register` with a JSON body
containing `username`, `password`, `email` and optional `first_name` and
`last_name`. The user is created in Keycloak and a linked entry is stored in the
local database.

When using `docker-compose up` a helper service runs `scripts/bootstrap_keycloak.py`
after Keycloak starts to create a demo account automatically. You can log in
with `demo` / `demo` immediately.

## Schema

The full database schema generated from the models is documented in [SCHEMA.md](SCHEMA.md).

## Lambert coordinates

Zones and parcels accept Lambert Nord Maroc coordinates when created or edited.
The admin interface lets you add or remove coordinate rows so an unlimited
number of `x y` pairs can be entered. You may also send a newline or semicolon
separated string to the API.  The polygon is closed automatically and converted
to WGS84 before storing it in the database.

## JavaScript implementation

The web interface relies entirely on vanilla JavaScript with no frameworks. All interactions including CRUD forms and map controls are handled using modern browser APIs. Map assets are loaded from a CDN using MapLibre so the app works without local dependencies. The default style comes from `https://demotiles.maplibre.org/style.json`.

The home page map loads zone geometries from `/map/zones` and parcel outlines
from `/map/parcels`. Each zone is drawn with a centroid marker so visitors can
quickly locate available areas while parcel boundaries are also visible for
reference.
