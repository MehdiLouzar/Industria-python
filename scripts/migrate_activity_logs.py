"""Migrer la table activity_logs pour Keycloak."""
from app import create_app, db

def main():
    app = create_app()
    with app.app_context():
        try:
            # Migration de la structure
            db.engine.execute("""
                -- Supprimer l'ancienne contrainte FK
                ALTER TABLE activity_logs 
                DROP CONSTRAINT IF EXISTS activity_logs_user_id_fkey;
                
                -- Supprimer l'ancienne colonne user_id
                ALTER TABLE activity_logs 
                DROP COLUMN IF EXISTS user_id;
                
                -- Ajouter les nouvelles colonnes Keycloak
                ALTER TABLE activity_logs 
                ADD COLUMN IF NOT EXISTS user_sub VARCHAR(255) NOT NULL DEFAULT 'unknown',
                ADD COLUMN IF NOT EXISTS user_email VARCHAR(255) NOT NULL DEFAULT 'unknown@example.com',
                ADD COLUMN IF NOT EXISTS user_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS user_roles TEXT,
                ADD COLUMN IF NOT EXISTS target_type VARCHAR(50) NOT NULL DEFAULT 'unknown',
                ADD COLUMN IF NOT EXISTS target_id VARCHAR(50),
                ADD COLUMN IF NOT EXISTS target_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS details TEXT,
                ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45),
                ADD COLUMN IF NOT EXISTS user_agent TEXT;
                
                -- Renommer action si besoin
                -- ALTER TABLE activity_logs RENAME COLUMN target TO action_details;
            """)
            
            print("✅ Activity logs migration completed")
            
        except Exception as exc:
            print(f"❌ Migration failed: {exc}")
            db.session.rollback()

if __name__ == "__main__":
    main()