from .services.auth_service import AuthService, require_auth, require_role, require_any_role

auth_service = AuthService()

# Exposer les décorateurs
__all__ = ['auth_service', 'require_auth', 'require_role', 'require_any_role']