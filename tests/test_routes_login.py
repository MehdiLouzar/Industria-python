from unittest.mock import patch, MagicMock

from app.decorators import auth_service


def test_login_route(app):
    svc = MagicMock()
    svc.login.return_value = {'access_token': 'abc'}
    with patch('app.routes.LoginService', return_value=svc):
        client = app.test_client()
        resp = client.post('/login', json={'username': 'u', 'password': 'p'})
        assert resp.status_code == 200
        assert resp.get_json() == {'access_token': 'abc'}


def test_logout_route(app):
    svc = MagicMock()
    svc.logout.return_value = {}
    with patch('app.decorators.auth_service.authenticate_request') as auth_call, \
         patch('app.routes.LoginService', return_value=svc):
        auth_call.return_value = {}
        client = app.test_client()
        resp = client.post('/logout', json={'refresh_token': 'r'})
        assert resp.status_code == 200
        assert resp.get_json()['message'] == 'Logged out'
        svc.logout.assert_called_with('r')
