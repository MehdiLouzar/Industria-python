"""Setup roles in Keycloak and assign them to demo user."""
from app.services.keycloak_admin_service import KeycloakAdminService

def main():
    svc = KeycloakAdminService()
    try:
        # Créer les rôles de base
        roles = [
            ("admin", "Administrateur système"),
            ("manager", "Gestionnaire"),
            ("user", "Utilisateur standard")
        ]
        
        for role_name, description in roles:
            if not svc.role_exists(role_name):
                svc.create_role(role_name, description)
                print(f"✅ Created role: {role_name}")
            else:
                print(f"ℹ️ Role {role_name} already exists")

        # Assigner le rôle admin à l'utilisateur demo
        users = svc.keycloak_admin.get_users({"username": "demo"})
        if users:
            user_id = users[0]["id"]
            svc.assign_role_to_user(user_id, "admin")
            print("✅ Assigned admin role to demo user")
        else:
            print("⚠️ Demo user not found")

    except Exception as exc:
        print(f"❌ Setup roles failed: {exc}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()