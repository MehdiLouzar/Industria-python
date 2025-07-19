"""Create default Keycloak client, roles and users automatically."""
import os
import time
from app.services.keycloak_admin_service import KeycloakAdminService

def wait_for_keycloak(max_retries=30, delay=5):
    """Attendre que Keycloak soit complètement prêt."""
    for attempt in range(max_retries):
        try:
            svc = KeycloakAdminService()
            if svc.keycloak_admin:
                print(f"✅ Keycloak is ready (attempt {attempt + 1})")
                return svc
            else:
                print(f"⏳ Keycloak not ready, attempt {attempt + 1}/{max_retries}")
        except Exception as e:
            print(f"⏳ Waiting for Keycloak... attempt {attempt + 1}/{max_retries}: {e}")
        
        time.sleep(delay)
    
    raise RuntimeError("Keycloak not available after maximum retries")

def setup_client(svc):
    """Configurer le client Keycloak avec secret prédéfini."""
    try:
        client_id = "industria"
        predefined_secret = "aIq8Fhb6mvS8FCVYEzEzA1wuDmoK0MRD"  # Secret fixe
        
        if svc.client_exists(client_id):
            print("ℹ️ Client industria already exists")
            
            # Vérifier/mettre à jour le secret
            try:
                svc.update_client_secret(client_id, predefined_secret)
                print(f"✅ Client secret updated to predefined value")
            except Exception as e:
                print(f"⚠️ Could not update secret: {e}")
            
            return False
        
        # Créer le client avec le secret prédéfini
        svc.create_client_with_secret(
            client_id=client_id,
            name="Industria App",
            secret=predefined_secret,
            public_client=False,
            direct_access_grants_enabled=True,
            standard_flow_enabled=True,
            service_accounts_enabled=True
        )
        
        print(f"✅ Created client '{client_id}' with predefined secret")
        print(f"🔑 Client secret: {predefined_secret}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        raise
    
def setup_roles(svc):
    """Configurer les rôles realm."""
    roles_config = [
        ("admin", "Administrateur système - Accès complet"),
        ("manager", "Gestionnaire - Gestion des zones et parcelles"),
        ("user", "Utilisateur standard - Consultation et réservation")
    ]
    
    created_roles = []
    try:
        for role_name, description in roles_config:
            if not svc.role_exists(role_name):
                svc.create_role(role_name, description)
                print(f"✅ Created role: {role_name}")
                created_roles.append(role_name)
            else:
                print(f"ℹ️ Role {role_name} already exists")
        return created_roles
    except Exception as e:
        print(f"❌ Failed to create roles: {e}")
        raise

def setup_demo_users(svc):
    """Créer les utilisateurs de démonstration."""
    users_config = [
        {
            "username": "admin",
            "email": "admin@industria.ma",
            "first_name": "Admin",
            "last_name": "Système",
            "password": "admin123",
            "roles": ["admin"]
        },
        {
            "username": "manager",
            "email": "manager@industria.ma", 
            "first_name": "Manager",
            "last_name": "Zone",
            "password": "manager123",
            "roles": ["manager", "user"]
        },
        {
            "username": "demo",
            "email": "demo@industria.ma",
            "first_name": "Demo",
            "last_name": "User", 
            "password": "demo123",
            "roles": ["user"]
        }
    ]
    
    created_users = []
    try:
        for user_config in users_config:
            username = user_config["username"]
            if not svc.user_exists(username):
                # Créer l'utilisateur
                user_id = svc.create_user(
                    username=username,
                    email=user_config["email"],
                    first_name=user_config["first_name"],
                    last_name=user_config["last_name"],
                    password=user_config["password"]
                )
                
                # Assigner les rôles
                for role in user_config["roles"]:
                    try:
                        svc.assign_role_to_user(user_id, role)
                        print(f"✅ Assigned role '{role}' to user '{username}'")
                    except Exception as role_error:
                        print(f"⚠️ Could not assign role '{role}' to '{username}': {role_error}")
                
                print(f"✅ Created user: {username} ({user_config['email']})")
                created_users.append(username)
            else:
                print(f"ℹ️ User {username} already exists")
        
        return created_users
    except Exception as e:
        print(f"❌ Failed to create users: {e}")
        raise

def main():
    """Bootstrap complet de Keycloak."""
    print("🚀 Starting Keycloak bootstrap...")
    
    try:
        # 1. Attendre que Keycloak soit prêt
        print("⏳ Waiting for Keycloak to be ready...")
        svc = wait_for_keycloak()
        
        # 2. Configurer le client
        print("🔧 Setting up client...")
        setup_client(svc)
        
        # 3. Configurer les rôles
        print("👥 Setting up roles...")
        created_roles = setup_roles(svc)
        
        # 4. Créer les utilisateurs
        print("👤 Setting up demo users...")
        created_users = setup_demo_users(svc)
        
        # 5. Résumé
        print("\n🎉 Bootstrap completed successfully!")
        print("=" * 50)
        print("📋 SUMMARY:")
        print(f"   • Client 'industria' configured")
        print(f"   • Roles created: {len(created_roles)}")
        print(f"   • Users created: {len(created_users)}")
        print("\n🔑 DEMO ACCOUNTS:")
        print("   • Admin:   admin / admin123")
        print("   • Manager: manager / manager123") 
        print("   • User:    demo / demo123")
        print("=" * 50)
        
    except Exception as exc:
        print(f"❌ Bootstrap failed: {exc}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
