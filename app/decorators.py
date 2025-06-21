from functools import wraps
from flask import g, abort

from .services.auth_service import AuthService


auth_service = AuthService()


def login_required(f):
    """Require a valid JWT token for the wrapped route."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_service.authenticate_request()
        return f(*args, **kwargs)

    return wrapped


def roles_required(role: str):
    """Require the current user to have ``role``."""

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            payload = auth_service.authenticate_request()
            roles = payload.get("realm_access", {}).get("roles", [])
            if role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator

