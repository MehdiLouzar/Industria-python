import os
import requests


class LoginService:
    """Obtain and revoke tokens from Keycloak."""

    def __init__(self):
        issuer = os.environ.get("KEYCLOAK_ISSUER", "http://localhost:8080/realms/master")
        issuer = issuer.rstrip("/")
        self.token_endpoint = f"{issuer}/protocol/openid-connect/token"
        self.logout_endpoint = f"{issuer}/protocol/openid-connect/logout"
        # Default to the audience client used for token validation if no
        # specific client id is provided. This avoids login errors when the
        # `industria` client does not exist in a fresh Keycloak setup.
        self.client_id = os.environ.get(
            "KEYCLOAK_CLIENT_ID",
            os.environ.get("KEYCLOAK_AUDIENCE", "account"),
        )
        self.client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")

    def login(self, username: str, password: str) -> dict:
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": username,
            "password": password,
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret
        resp = requests.post(self.token_endpoint, data=data, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def logout(self, refresh_token: str) -> dict:
        data = {"client_id": self.client_id, "refresh_token": refresh_token}
        if self.client_secret:
            data["client_secret"] = self.client_secret
        resp = requests.post(self.logout_endpoint, data=data, timeout=5)
        resp.raise_for_status()
        return resp.json()
