#!/bin/bash
set -e

echo "🚀 Rebuilding Industria with automated setup..."

# Arrêter et nettoyer
echo "🧹 Cleaning up existing containers..."
docker-compose down -v
docker system prune -f

# Rebuilder et démarrer
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Attendre et vérifier
echo "⏳ Waiting for services to be ready..."
sleep 30

# Vérifier le statut
echo "📊 Checking service status..."
docker-compose ps

# Vérifier les logs du bootstrap
echo "📝 Bootstrap logs:"
docker-compose logs keycloak_bootstrap

echo "✅ Setup complete! You can now:"
echo "   🌐 Access app: http://localhost:8000"
echo "   🔐 Access Keycloak: http://localhost:8080"
echo "   🔑 Login with: admin/admin123, manager/manager123, or demo/demo123"