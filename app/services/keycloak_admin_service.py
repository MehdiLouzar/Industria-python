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
    
    def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str) -> str:
        """Crée un utilisateur et retourne son ID."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        
        user = {
            "email": email,
            "username": username,
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
        
        user_id = self.keycloak_admin.create_user(user)
        return user_id

    def role_exists(self, role_name: str) -> bool:
        """Vérifie si un rôle realm existe."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        try:
            role = self.keycloak_admin.get_realm_role(role_name)
            return role is not None
        except:
            return False

    def create_role(self, role_name: str, description: str = None) -> None:
        """Crée un rôle realm."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        
        payload = {
            "name": role_name,
            "description": description or f"Role {role_name}"
        }
        self.keycloak_admin.create_realm_role(payload)

    def assign_role_to_user(self, user_id: str, role_name: str) -> None:
        """Assigne un rôle realm à un utilisateur."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        
        role = self.keycloak_admin.get_realm_role(role_name)
        self.keycloak_admin.assign_realm_roles(user_id, [role])
    
    def create_client_with_secret(
        self,
        client_id: str,
        name: str,
        secret: str,
        public_client: bool,
        direct_access_grants_enabled: bool,
        standard_flow_enabled: bool,
        service_accounts_enabled: bool,
    ) -> None:
        """Créer un client avec un secret prédéfini."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        
        # Créer le client
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
            "secret": secret,  # Définir le secret
        }
        
        self.keycloak_admin.create_client(client_representation)

    def update_client_secret(self, client_id: str, new_secret: str) -> None:
        """Mettre à jour le secret d'un client."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        
        # Récupérer l'ID interne du client
        clients = self.keycloak_admin.get_clients()
        client = next((c for c in clients if c["clientId"] == client_id), None)
        
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Mettre à jour le secret
        self.keycloak_admin.update_client(client["id"], {"secret": new_secret})

    def get_client_secret(self, client_id: str) -> str:
        """Récupérer le secret d'un client."""
        if not self.keycloak_admin:
            raise RuntimeError("Keycloak admin not initialized")
        
        # Récupérer l'ID interne du client
        clients = self.keycloak_admin.get_clients()
        client = next((c for c in clients if c["clientId"] == client_id), None)
        
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Récupérer le secret
        secret_data = self.keycloak_admin.get_client_secrets(client["id"])
        return secret_data["value"]