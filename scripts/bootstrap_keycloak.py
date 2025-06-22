"""Create a default user in Keycloak if it doesn't already exist."""
from app.services.keycloak_admin_service import KeycloakAdminService


def main():
    svc = KeycloakAdminService()
    try:
        if not svc.user_exists("demo"):
            svc.create_user(
                username="demo",
                email="demo@example.com",
                first_name="Demo",
                last_name="User",
                password="demo"
            )
            print("Created demo user in Keycloak")
        else:
            print("Demo user already exists")
    except Exception as exc:
        print(f"Could not create demo user: {exc}")


if __name__ == "__main__":
    main()
