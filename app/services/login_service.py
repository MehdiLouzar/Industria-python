# app/services.py

import os
import requests
from typing import Dict

class LoginService:

    def __init__(self):
        issuer = os.environ.get("KEYCLOAK_ISSUER", "http://localhost:8080/realms/master").rstrip("/")
        self.issuer = issuer
        self.realm = issuer.rsplit("/", 1)[-1]

        self.token_endpoint = f"{issuer}/protocol/openid-connect/token"
        self.logout_endpoint = f"{issuer}/protocol/openid-connect/logout"
        self.userinfo_endpoint = f"{issuer}/protocol/openid-connect/userinfo"

        self.client_id = os.environ.get("KEYCLOAK_CLIENT_ID", "industria")
        self.client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")

    def login(self, username: str, password: str) -> Dict[str, str]:
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": username,
            "password": password,
            "scope": "openid",               # ← Ajout du scope openid
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret

        resp = requests.post(self.token_endpoint, data=data, timeout=5)
        if not resp.ok:
            print(f"[LoginService] status_code={resp.status_code}, body={resp.text}")
            resp.raise_for_status()
        return resp.json()

    def logout(self, refresh_token: str) -> dict:
        data = {"client_id": self.client_id, "refresh_token": refresh_token}
        if self.client_secret:
            data["client_secret"] = self.client_secret

        resp = requests.post(self.logout_endpoint, data=data, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def userinfo(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(self.userinfo_endpoint, headers=headers, timeout=5)
        resp.raise_for_status()
        return resp.json()
