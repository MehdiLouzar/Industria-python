"""Service pour logger les activités utilisateur."""
from flask import request, g
from ..models.activity_log import ActivityLog
from ..models.keycloak_user import KeycloakUser
from .. import db

class ActivityLogger:
    """Service de logging des activités utilisateur."""
    
    @staticmethod
    def log_activity(action: str, target_type: str, target_id=None, target_name=None, details=None):
        """Logger une activité utilisateur."""
        try:
            # Récupérer l'utilisateur actuel
            user = KeycloakUser.current()
            if not user:
                return  # Pas d'utilisateur connecté, on ne log pas
            
            # Créer le log
            activity_log = ActivityLog(
                action=action,
                target_type=target_type,
                target_id=str(target_id) if target_id else None,
                target_name=target_name,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            # Définir les infos utilisateur
            activity_log.set_user_from_keycloak(user)
            
            # Définir les détails si fournis
            if details:
                activity_log.set_details(details)
            
            # Sauvegarder
            db.session.add(activity_log)
            db.session.commit()
            
        except Exception as e:
            # En cas d'erreur, on ne fait pas planter l'app
            print(f"Erreur lors du logging d'activité: {e}")
            db.session.rollback()
    
    @staticmethod
    def log_zone_created(zone):
        """Logger la création d'une zone."""
        ActivityLogger.log_activity(
            action="CREATE",
            target_type="Zone",
            target_id=zone.id,
            target_name=zone.name,
            details={
                "zone_type": zone.zone_type.name if zone.zone_type else None,
                "region": zone.region.name if zone.region else None,
                "total_area": float(zone.total_area) if zone.total_area else None
            }
        )
    
    @staticmethod
    def log_zone_updated(zone, changed_fields=None):
        """Logger la modification d'une zone."""
        ActivityLogger.log_activity(
            action="UPDATE",
            target_type="Zone",
            target_id=zone.id,
            target_name=zone.name,
            details={
                "changed_fields": changed_fields or [],
                "zone_type": zone.zone_type.name if zone.zone_type else None
            }
        )
    
    @staticmethod
    def log_zone_deleted(zone):
        """Logger la suppression d'une zone."""
        ActivityLogger.log_activity(
            action="DELETE",
            target_type="Zone",
            target_id=zone.id,
            target_name=zone.name,
            details={
                "zone_type": zone.zone_type.name if zone.zone_type else None,
                "had_parcels": len(zone.parcels) if zone.parcels else 0
            }
        )
    
    @staticmethod
    def log_parcel_reserved(parcel, appointment):
        """Logger la réservation d'une parcelle."""
        ActivityLogger.log_activity(
            action="RESERVE",
            target_type="Parcel",
            target_id=parcel.id,
            target_name=parcel.name,
            details={
                "zone_name": parcel.zone.name if parcel.zone else None,
                "appointment_id": appointment.id,
                "requested_date": appointment.requested_date.isoformat() if appointment.requested_date else None
            }
        )
    
    @staticmethod
    def log_appointment_approved(appointment):
        """Logger l'approbation d'un rendez-vous."""
        ActivityLogger.log_activity(
            action="APPROVE",
            target_type="Appointment",
            target_id=appointment.id,
            target_name=f"RDV {appointment.id}",
            details={
                "parcel_name": appointment.parcel.name if appointment.parcel else None,
                "company_name": appointment.company_name,
                "contact_phone": appointment.contact_phone
            }
        )
    
    @staticmethod
    def log_user_login():
        """Logger la connexion d'un utilisateur."""
        ActivityLogger.log_activity(
            action="LOGIN",
            target_type="System",
            details={
                "login_time": datetime.utcnow().isoformat()
            }
        )