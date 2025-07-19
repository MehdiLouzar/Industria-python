from datetime import datetime
from .. import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    # === INFORMATIONS UTILISATEUR KEYCLOAK ===
    user_sub = db.Column(db.String(255), nullable=False)  # ID Keycloak (sub)
    user_email = db.Column(db.String(255), nullable=False)  # Email pour affichage
    user_name = db.Column(db.String(255), nullable=True)   # Nom complet pour affichage
    user_roles = db.Column(db.Text, nullable=True)         # Rôles JSON stringifié
    
    # === INFORMATIONS DE L'ACTION ===
    action = db.Column(db.Text, nullable=False)            # CREATE, UPDATE, DELETE, VIEW
    target_type = db.Column(db.String(50), nullable=False) # Zone, Parcel, Appointment, etc.
    target_id = db.Column(db.String(50), nullable=True)    # ID de l'objet ciblé
    target_name = db.Column(db.String(255), nullable=True) # Nom de l'objet pour affichage
    
    # === MÉTADONNÉES ===
    details = db.Column(db.Text, nullable=True)            # Détails additionnels (JSON)
    ip_address = db.Column(db.String(45), nullable=True)   # Adresse IP de l'utilisateur
    user_agent = db.Column(db.Text, nullable=True)         # User agent du navigateur
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ActivityLog {self.user_email}: {self.action} {self.target_type}>'
    
    @property
    def user_roles_list(self):
        """Retourne les rôles sous forme de liste."""
        if not self.user_roles:
            return []
        try:
            import json
            return json.loads(self.user_roles)
        except:
            return []
    
    def set_user_from_keycloak(self, user):
        """Définir les infos utilisateur depuis un KeycloakUser."""
        import json
        self.user_sub = user.sub
        self.user_email = user.email
        self.user_name = user.full_name
        self.user_roles = json.dumps(user.roles or [])
    
    def set_details(self, details_dict):
        """Définir les détails sous forme de dictionnaire."""
        if details_dict:
            import json
            self.details = json.dumps(details_dict)
    
    def get_details(self):
        """Récupérer les détails sous forme de dictionnaire."""
        if not self.details:
            return {}
        try:
            import json
            return json.loads(self.details)
        except:
            return {}
    
    def to_dict(self):
        """Convertir en dictionnaire pour l'API."""
        return {
            'id': self.id,
            'user': {
                'sub': self.user_sub,
                'email': self.user_email,
                'name': self.user_name,
                'roles': self.user_roles_list
            },
            'action': self.action,
            'target': {
                'type': self.target_type,
                'id': self.target_id,
                'name': self.target_name
            },
            'details': self.get_details(),
            'metadata': {
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None
            }
        }