from flask import request, abort, g
from functools import wraps
from .token_service import TokenService
from ..models.keycloak_user import KeycloakUser

token_service = TokenService()

class AuthService:
    def __init__(self, token_svc: TokenService = token_service):
        self.token_service = token_svc

    def authenticate_request(self) -> KeycloakUser:
        """Authentifie et retourne un utilisateur Keycloak."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, "Missing or invalid authorization header")
        
        token = auth_header.split()[1]
        try:
            payload = self.token_service.verify(token)
            user = KeycloakUser.from_token(payload)
            g.current_user = user
            g.token_payload = payload
            return user
        except Exception as exc:
            abort(401, description=f"Token validation failed: {str(exc)}")

def require_auth(f):
    """Décorateur pour exiger une authentification."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_service = AuthService()
        auth_service.authenticate_request()
        return f(*args, **kwargs)
    return wrapper

def require_role(role: str):
    """Décorateur pour exiger un rôle spécifique."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_service = AuthService()
            user = auth_service.authenticate_request()
            if not user.has_role(role):
                abort(403, f"Role '{role}' required")
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_any_role(*roles: str):
    """Décorateur pour exiger au moins un des rôles."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_service = AuthService()
            user = auth_service.authenticate_request()
            if not user.has_any_role(*roles):
                abort(403, f"One of these roles required: {', '.join(roles)}")
            return f(*args, **kwargs)
        return wrapper
    return decorator