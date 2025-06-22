"""Create default Keycloak client and user if they don't already exist."""
import os
from app.services.keycloak_admin_service import KeycloakAdminService

# Charger l'application Flask
from app import create_app, db
from app.models.user import User

def main():
    app = create_app()
    with app.app_context():
        svc = KeycloakAdminService()
        try:
            if not svc.client_exists("industria"):
                svc.create_client(
                    client_id="industria",
                    name="Industria App",
                    public_client=False,
                    direct_access_grants_enabled=True,
                    standard_flow_enabled=True,
                    service_accounts_enabled=True
                )
                print("✅ Created industria client in Keycloak")
            else:
                print("ℹ️ Client industria already exists")

            keycloak_username = "demo@example.com"
            if not svc.user_exists(keycloak_username):
                svc.create_user(
                    username=keycloak_username,
                    email=keycloak_username,
                    first_name="Demo",
                    last_name="User",
                    password="demo"
                )
                print("✅ Created demo user in Keycloak")
            else:
                print("ℹ️ Demo user already exists in Keycloak")

            existing_user = User.query.filter_by(email=keycloak_username).first()
            if not existing_user:
                user = User(
                    first_name="Demo",
                    last_name="User",
                    email=keycloak_username,
                    is_active=True,
                    user_role=1 
                )
                db.session.add(user)
                db.session.commit()
                print("✅ Created demo user in Flask DB")
            else:
                print("ℹ️ Demo user already exists in Flask DB")

        except Exception as exc:
            print(f"❌ Could not bootstrap Keycloak and DB: {exc}")


if __name__ == "__main__":
    main()
