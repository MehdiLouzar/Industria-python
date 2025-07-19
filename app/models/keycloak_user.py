"""Modèle utilisateur basé sur Keycloak uniquement."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from flask import g

@dataclass
class KeycloakUser:
    """Utilisateur basé sur les données Keycloak uniquement."""
    sub: str  # Subject (ID unique Keycloak)
    preferred_username: str
    email: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    roles: List[str] = None
    raw_token: Dict[str, Any] = None
    
    @classmethod
    def from_token(cls, token_payload: dict) -> 'KeycloakUser':
        """Créer un utilisateur à partir du token JWT."""
        realm_access = token_payload.get('realm_access', {})
        roles = realm_access.get('roles', [])
        
        return cls(
            sub=token_payload.get('sub'),
            preferred_username=token_payload.get('preferred_username'),
            email=token_payload.get('email'),
            given_name=token_payload.get('given_name'),
            family_name=token_payload.get('family_name'),
            roles=roles,
            raw_token=token_payload
        )
    
    @classmethod
    def current(cls) -> Optional['KeycloakUser']:
        """Obtenir l'utilisateur actuel depuis le contexte Flask."""
        return getattr(g, 'current_user', None)
    
    # Propriétés de rôle
    @property
    def is_admin(self) -> bool:
        return 'admin' in (self.roles or [])
    
    @property
    def is_manager(self) -> bool:
        return 'manager' in (self.roles or [])
    
    @property
    def is_user(self) -> bool:
        return 'user' in (self.roles or [])
    
    # Propriétés d'affichage
    @property
    def full_name(self) -> str:
        if self.given_name and self.family_name:
            return f"{self.given_name} {self.family_name}"
        return self.preferred_username or self.email
    
    @property
    def display_name(self) -> str:
        """Nom à afficher dans l'interface."""
        return self.full_name
    
    @property
    def initials(self) -> str:
        """Initiales pour les avatars."""
        if self.given_name and self.family_name:
            return f"{self.given_name[0]}{self.family_name[0]}".upper()
        elif self.preferred_username:
            return self.preferred_username[:2].upper()
        return self.email[:2].upper()
    
    # Méthodes utilitaires
    def has_role(self, role: str) -> bool:
        """Vérifie si l'utilisateur a un rôle spécifique."""
        return role in (self.roles or [])
    
    def has_any_role(self, *roles: str) -> bool:
        """Vérifie si l'utilisateur a au moins un des rôles."""
        return any(self.has_role(role) for role in roles)
    
    def has_all_roles(self, *roles: str) -> bool:
        """Vérifie si l'utilisateur a tous les rôles."""
        return all(self.has_role(role) for role in roles)
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire pour l'API."""
        return {
            'id': self.sub,
            'username': self.preferred_username,
            'email': self.email,
            'full_name': self.full_name,
            'given_name': self.given_name,
            'family_name': self.family_name,
            'roles': self.roles,
            'is_admin': self.is_admin,
            'is_manager': self.is_manager
        }
    
    def __repr__(self):
        return f"<KeycloakUser {self.email} ({self.preferred_username})>"