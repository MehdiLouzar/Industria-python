"""Décorateurs pour logger automatiquement les activités."""
from functools import wraps
from ..services.activity_logger import ActivityLogger

def log_activity(action: str, target_type: str):
    """Décorateur pour logger automatiquement une activité."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Exécuter la fonction
            result = f(*args, **kwargs)
            
            # Logger l'activité après succès
            try:
                # Extraire les infos du résultat si possible
                target_id = None
                target_name = None
                
                if hasattr(result, 'id'):
                    target_id = result.id
                if hasattr(result, 'name'):
                    target_name = result.name
                
                ActivityLogger.log_activity(action, target_type, target_id, target_name)
            except:
                pass  # Ne pas faire planter en cas d'erreur de logging
            
            return result
        return wrapper
    return decorator