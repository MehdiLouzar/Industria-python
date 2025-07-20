from unittest.mock import patch, MagicMock


def test_register_route(app):
    svc = MagicMock()
    svc.create_user.return_value = 'kc-id'
    with patch('app.routes.KeycloakAdminService', return_value=svc):
        client = app.test_client()
        resp = client.post('/register', json={
            'username': 'user',
            'password': 'pass',
            'email': 'user@example.com',
            'first_name': 'User',
            'last_name': 'Test'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['email'] == 'user@example.com'
        svc.create_user.assert_called_once()
