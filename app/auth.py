from flask_login import UserMixin

class SessionUser(UserMixin):
    def __init__(self, info: dict):
        self.id = info.get('sub')  # ID unique Keycloak
        self.preferred_username = info.get('preferred_username')
        self.email = info.get('email')
        self.given_name = info.get('given_name')
        self.family_name = info.get('family_name')
        self.info = info
        
        # Extraire les rôles realm
        realm_access = info.get('realm_access', {})
        self.roles = realm_access.get('roles', [])

    @property
    def is_admin(self):
        """Vérifie si l'utilisateur a le rôle admin."""
        return 'admin' in self.roles

    @property
    def is_manager(self):
        """Vérifie si l'utilisateur a le rôle manager.""" 
        return 'manager' in self.roles

    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        if self.given_name and self.family_name:
            return f"{self.given_name} {self.family_name}"
        return self.preferred_username or self.email

    def __repr__(self):
        return f"<SessionUser {self.email}>"