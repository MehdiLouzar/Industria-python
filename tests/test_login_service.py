from unittest.mock import patch, MagicMock

from app.services.login_service import LoginService


def test_login_service_login():
    svc = LoginService()
    with patch('app.services.login_service.requests.post') as post:
        resp = MagicMock()
        resp.json.return_value = {'access_token': 'abc'}
        resp.raise_for_status.return_value = None
        post.return_value = resp
        result = svc.login('user', 'pass')
        post.assert_called_once()
        assert result == {'access_token': 'abc'}


def test_login_service_logout():
    svc = LoginService()
    with patch('app.services.login_service.requests.post') as post:
        resp = MagicMock()
        resp.json.return_value = {}
        resp.raise_for_status.return_value = None
        post.return_value = resp
        result = svc.logout('refresh')
        post.assert_called_once()
        assert result == {}
