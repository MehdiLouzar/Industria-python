import os
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakAuthenticationError


class KeycloakAdminService:
    def __init__(self):
        self.server_url = os.getenv("KEYCLOAK_SERVER_URL", "http://keycloak:8080")
        self.realm_name = os.getenv("KEYCLOAK_REALM", "master")
        self.username = os.getenv("KEYCLOAK_ADMIN", "admin")
        self.password = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
        self.client_id = "admin-cli"

        try:
            self.keycloak_admin = KeycloakAdmin(
                server_url=f"{self.server_url}/",
                username=self.username,
                password=self.password,
                realm_name=self.realm_name,
                client_id=self.client_id,
                verify=True
            )
            print("✅ Connected to Keycloak admin API successfully.")
        except KeycloakAuthenticationError as e:
            print(f"❌ Authentication failed with Keycloak: {e}")
            self.keycloak_admin = None
        except Exception as e:
            print(f"❌ Failed to connect to Keycloak: {e}")
            self.keycloak_admin = None

    def user_exists(self, username: str) -> bool:
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        users = self.keycloak_admin.get_users({"username": username})
        return any(user["username"] == username for user in users)

    def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str) -> None:
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        user = {
            "email": email,
            "username": email,  # 👈 Important : email comme username
            "enabled": True,
            "firstName": first_name,
            "lastName": last_name,
            "emailVerified": True,
            "credentials": [{
                "type": "password",
                "value": password,
                "temporary": False
            }]
        }
        self.keycloak_admin.create_user(user)

    def client_exists(self, client_id: str) -> bool:
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        clients = self.keycloak_admin.get_clients()
        return any(client["clientId"] == client_id for client in clients)

    def create_client(
        self,
        client_id: str,
        name: str,
        public_client: bool,
        direct_access_grants_enabled: bool,
        standard_flow_enabled: bool,
        service_accounts_enabled: bool,
    ) -> None:
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        client_representation = {
            "clientId": client_id,
            "name": name,
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": public_client,
            "redirectUris": ["*"],
            "directAccessGrantsEnabled": direct_access_grants_enabled,
            "standardFlowEnabled": standard_flow_enabled,
            "serviceAccountsEnabled": service_accounts_enabled,
            "fullScopeAllowed": True,
        }
        self.keycloak_admin.create_client(client_representation)
