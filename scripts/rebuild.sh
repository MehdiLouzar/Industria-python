#!/bin/bash
set -e

# Rebuild and start containers sequentially

echo "🚀 Rebuilding Industria with automated setup..."


echo "🧹 Cleaning up existing containers..."
docker compose down -v
docker system prune -f

echo "🔨 Building images..."
docker compose build --no-cache

echo "🐘 Starting database..."
docker compose up -d db

echo "⏳ Waiting for PostgreSQL to accept connections..."
docker compose exec db bash -c 'until pg_isready -U postgres; do sleep 2; done'

echo "🐍 Starting Flask app..."
docker compose up -d flask_app

echo "⏳ Allowing Flask to initialize tables..."
sleep 15

echo "📄 Populating database..."
docker compose run --rm init_db

echo "🔐 Starting Keycloak..."
docker compose up -d keycloak keycloak_bootstrap

echo "📊 Final service status:"
docker compose ps

echo "📝 Bootstrap logs:"
docker compose logs keycloak_bootstrap

echo "✅ Setup complete! You can now:"
echo "   🌐 Access app: http://localhost:8000"
echo "   🔐 Access Keycloak: http://localhost:8080"
echo "   🔑 Login with: admin/admin123, manager/manager123, or demo/demo123"

