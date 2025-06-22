# app/auth.py
from flask_login import UserMixin

class SessionUser(UserMixin):
    def __init__(self, info: dict):
        # info == session['user'] renvoyé par Keycloak userinfo
        self.id = info.get('sub')  # identifiant unique
        self.preferred_username = info.get('preferred_username')
        self.info = info           # tu peux stocker d’autres attributs si tu veux
