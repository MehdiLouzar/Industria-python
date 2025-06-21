import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, g

from app.services.token_service import TokenService
from app.services.auth_service import AuthService


def test_token_service_verify():
    token = 'abc'
    key = MagicMock()
    key.key = 'secret'
    with patch('app.services.token_service.PyJWKClient') as pjwk, \
         patch('app.services.token_service.jwt.decode', return_value={'sub': 'u1'}):
        client_instance = pjwk.return_value
        client_instance.get_signing_key_from_jwt.return_value = key
        svc = TokenService()
        payload = svc.verify(token)
        assert payload == {'sub': 'u1'}
        client_instance.get_signing_key_from_jwt.assert_called_with(token)


def test_auth_service_authenticate_request(monkeypatch):
    app = Flask(__name__)
    token_svc = MagicMock()
    token_svc.verify.return_value = {'sub': 'u1'}
    auth = AuthService(token_svc)
    with app.test_request_context(headers={'Authorization': 'Bearer t'}):
        payload = auth.authenticate_request()
        assert payload == {'sub': 'u1'}
        assert g.token_payload == {'sub': 'u1'}
        token_svc.verify.assert_called_with('t')
