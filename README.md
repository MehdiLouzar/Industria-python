# Industria Python

This repository provides a minimal example of how to containerize a Flask application with Docker Compose. It also includes a PostgreSQL database with PostGIS and a Keycloak identity provider.

## Structure

```
./flask_app/
    app.py            # Flask application
    requirements.txt  # Python dependencies
    Dockerfile        # Container image for the Flask app
./db/init/script.sql  # Optional SQL script executed on DB start
./docker-compose.yml  # Compose configuration
Keycloak runs in its own container and exposes port 8080
```

## Usage

Build and start the containers:

```bash
docker-compose up --build
```

The Flask application will be available at `http://localhost:8000/`, the PostgreSQL database at `localhost:5432`, and Keycloak at `http://localhost:8080/`.

