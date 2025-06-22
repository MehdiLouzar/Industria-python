import os
import requests


class KeycloakAdminService:
    """Interact with Keycloak's admin API to manage users."""

    def __init__(self):
        base = os.environ.get("KEYCLOAK_BASE_URL", "http://localhost:8080")
        realm = os.environ.get("KEYCLOAK_REALM", "master")
        self.realm = realm
        self.base_url = base.rstrip('/')
        self.token_endpoint = f"{self.base_url}/realms/{realm}/protocol/openid-connect/token"
        self.users_endpoint = f"{self.base_url}/admin/realms/{realm}/users"
        self.admin_user = os.environ.get("KEYCLOAK_ADMIN", "admin")
        self.admin_password = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "admin")

    def _admin_token(self) -> str:
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.admin_user,
            "password": self.admin_password,
        }
        resp = requests.post(self.token_endpoint, data=data, timeout=5)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str) -> str:
        token = self._admin_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "username": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "credentials": [
                {"type": "password", "value": password, "temporary": False}
            ],
        }
        resp = requests.post(self.users_endpoint, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
        # Keycloak returns location header with user id
        location = resp.headers.get("Location", "")
        return location.rsplit('/', 1)[-1] if location else ""
