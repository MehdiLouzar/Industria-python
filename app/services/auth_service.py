
from flask import request, abort, g

from .token_service import TokenService


token_service = TokenService()


class AuthService:
    """Authenticate incoming requests using Keycloak JWTs."""

    def __init__(self, token_svc: TokenService = token_service):
        self.token_service = token_svc

    def authenticate_request(self) -> dict:
        """Validate Authorization header and store payload in ``g``."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401)
        token = auth_header.split()[1]
        try:
            payload = self.token_service.verify(token)
        except Exception as exc:  # pragma: no cover - passthrough errors
            abort(401, description=str(exc))
        g.token_payload = payload
        return payload
