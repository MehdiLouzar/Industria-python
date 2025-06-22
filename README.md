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
./db/init/script.sql    # Optional SQL script executed on DB start
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
variables `KEYCLOAK_ISSUER` and `KEYCLOAK_AUDIENCE` (see `docker-compose.yml`).
Routes are protected using these tokens via the provided decorators.

To register a new account, send a POST request to `/register` with a JSON body
containing `username`, `password`, `email` and optional `first_name` and
`last_name`. The user is created in Keycloak and a linked entry is stored in the
local database.

You can also run `python scripts/bootstrap_keycloak.py` once the Keycloak
container is up to create a demo user automatically.

## Schema

The full database schema generated from the models is documented in [SCHEMA.md](SCHEMA.md).
