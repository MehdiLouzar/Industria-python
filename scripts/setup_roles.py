"""Setup roles in Keycloak and assign them to the demo user."""

from app.services.keycloak_admin_service import KeycloakAdminService


def main():
    svc = KeycloakAdminService()
    try:
        roles = [
            ("admin", "Administrateur système"),
            ("manager", "Gestionnaire"),
            ("user", "Utilisateur standard"),
        ]

        for name, desc in roles:
            if not svc.role_exists(name):
                svc.create_role(name, desc)
                print(f"✅ Created role: {name}")
            else:
                print(f"ℹ️ Role {name} already exists")

        users = svc.keycloak_admin.get_users({"username": "demo"})
        if users:
            svc.assign_role_to_user(users[0]["id"], "admin")
            print("✅ Assigned admin role to demo user")
        else:
            print("⚠️ Demo user not found")

    except Exception as exc:
        print(f"❌ Setup roles failed: {exc}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

