from app import create_app


def test_login_form_page(app):
    client = app.test_client()
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'Ravis de vous revoir' in resp.data
