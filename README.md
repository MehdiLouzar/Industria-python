# Industria Python

This repository provides a minimal example of how to containerize a Flask application with Docker Compose. It also includes a PostgreSQL database with PostGIS and a Keycloak identity provider.

## Structure

```
./app/                   # Flask application package
    __init__.py         # create_app and blueprint registration
    routes.py           # application routes
    models/             # business classes
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
