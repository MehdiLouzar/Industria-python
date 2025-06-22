
import os
import jwt
from jwt import PyJWKClient


class TokenService:

    def __init__(self):
        issuer = os.environ.get("KEYCLOAK_ISSUER", "http://localhost:8080/realms/master")
        self.issuer = issuer.rstrip("/")
        self.audience = os.environ.get("KEYCLOAK_AUDIENCE")
        jwks_url = f"{self.issuer}/protocol/openid-connect/certs"
        self.jwks_client = PyJWKClient(jwks_url)

    def verify(self, token: str) -> dict:
        """Validate a JWT and return its payload."""
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.audience,
            issuer=self.issuer,
        )
        return data
