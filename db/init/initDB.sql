-- db/init/initDB.sql
-- Population des données de démonstration pour Industria
-- Les tables sont créées par Flask/SQLAlchemy

-- Vérifier que PostGIS est disponible
CREATE EXTENSION IF NOT EXISTS postgis;

-- Fonction pour vider les tables dans le bon ordre (respecting FK constraints)
DO
$$
DECLARE
  -- Tables dans l'ordre inverse pour le nettoyage (enfants -> parents)
  tables text[] := ARRAY[
    'zone_activities', 'parcel_amenities', 'appointments', 'parcels',
    'zones', 'zone_types', 'activities', 'amenities',
    'appointment_status', 'regions', 'countries', 'activity_logs'
  ];
  tbl text;
BEGIN
  -- Attendre que les tables soient créées par Flask
  -- Cette fonction sera exécutée après Flask
  RAISE NOTICE 'Starting data population...';
  
  -- Nettoyer les données existantes si les tables existent
  FOREACH tbl IN ARRAY tables LOOP
    IF to_regclass('public.' || tbl) IS NOT NULL THEN
      EXECUTE format('TRUNCATE TABLE public.%I RESTART IDENTITY CASCADE', tbl);
      RAISE NOTICE 'Cleaned table: %', tbl;
    END IF;
  END LOOP;
END
$$;

-- Basic reference data
INSERT INTO countries (id, name, code) VALUES
  (1, 'Maroc', 'MA')
ON CONFLICT (id) DO NOTHING;

INSERT INTO zone_types (id, name) VALUES
  (1, 'privée'),
  (2, 'public')
ON CONFLICT (id) DO NOTHING;

INSERT INTO regions (id, name, country_id) VALUES
  (1, 'Tanger-Tétouan-Al Hoceïma', 1),
  (2, 'L''Oriental',              1),
  (3, 'Fès-Meknès',               1),
  (4, 'Rabat-Salé-Kénitra',       1),
  (5, 'Béni Mellal-Khénifra',     1),
  (6, 'Casablanca-Settat',        1),
  (7, 'Marrakech-Safi',           1),
  (8, 'Drâa-Tafilalet',           1),
  (9, 'Souss-Massa',              1),
  (10,'Guelmim-Oued Noun',        1),
  (11,'Laâyoune-Sakia El Hamra',  1),
  (12,'Dakhla-Oued Ed-Dahab',     1)
ON CONFLICT (id) DO NOTHING;

-- Supprimer l'insertion des roles - ils seront gérés par Keycloak

INSERT INTO amenities (id, amenities_key, label, icon) VALUES
  (1, 'electricity', 'Électricité', '<svg viewBox="0 0 24 24"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>'),
  (2, 'water', 'Eau potable', '<svg viewBox="0 0 24 24"><path d="M12 2c-5.33 4.55-8 8.48-8 11.8 0 4.98 3.8 8.2 8 8.2s8-3.22 8-8.2c0-3.32-2.67-7.25-8-11.8zM7.83 14c.37 0 .67.26.74.62.41 2.22 2.28 2.98 3.64 2.87.43-.02.79.32.79.75 0 .4-.32.73-.72.75-2.13.13-4.62-1.09-5.19-4.12a.75.75 0 01.74-.87z"/></svg>'),
  (3, 'fiber', 'Fibre optique', '<svg viewBox="0 0 24 24"><path d="M9.93 13.5h4.14L12 7.98zM20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-3.05 16.5l-1.14-3H8.19l-1.14 3H5.96l5.11-13h1.86l5.11 13h-1.09z"/></svg>'),
  (4, 'parking', 'Parking', '<svg viewBox="0 0 24 24"><path d="M13 3H6v18h4v-6h3c3.31 0 6-2.69 6-6s-2.69-6-6-6zm.2 8H10V7h3.2c1.1 0 2 .9 2 2s-.9 2-2 2z"/></svg>'),
  (5, 'security', 'Sécurité 24/7', '<svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>')
ON CONFLICT (id) DO UPDATE 
SET icon = EXCLUDED.icon;

INSERT INTO activities (id, activities_key, label, icon) VALUES
  (1, 'industry', 'Industrie', '<svg viewBox="0 0 24 24"><path d="M18 3v2h-2V3H8v2H6V3H2v18h4v-2h2v2h8v-2h2v2h4V3h-4zM8 17H6v-2h2v2zm0-4H6v-2h2v2zm0-4H6V7h2v2zm10 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V7h2v2z"/></svg>'),
  (2, 'logistics', 'Logistique', '<svg viewBox="0 0 24 24"><path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>'),
  (3, 'commerce', 'Commerce', '<svg viewBox="0 0 24 24"><path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/></svg>'),
  (4, 'services', 'Services', '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'),
  (5, 'technology', 'Technologie', '<svg viewBox="0 0 24 24"><path d="M20 18c1.1 0 1.99-.9 1.99-2L22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2h-4zM4 6h16v10H4V6z"/></svg>')
ON CONFLICT (id) DO UPDATE 
SET icon = EXCLUDED.icon;

INSERT INTO appointment_status (id, status_name) VALUES
  (1, 'Pending'),
  (2, 'Confirmed'), 
  (3, 'Canceled')
ON CONFLICT (id) DO NOTHING;

-- Ajouter une zone de démonstration (comme dans votre fichier original)
WITH ins AS (
  INSERT INTO spatial_entities (entity_type, name, description, geometry)
  VALUES (
    'zone', 'PIAJ', 'Zone générée automatiquement pour les tests',
    -- Conversion des coordonnées Lambert Nord Maroc (EPSG:26191) vers WGS84 (EPSG:4326)
    ST_Transform(
      ST_GeomFromText(
        'POLYGON((
          409201.18 369451.53,
          409639.39 368996.57,
          409763.12 368701.53,
          409854.56 368701.50,
          409874.98 368535.76,
          409901.57 368332.92,
          409954.02 368056.56,
          409957.84 368038.85,
          410025.04 367870.11,
          410201.81 367573.04,
          410291.56 367448.47,
          410374.16 367349.62,
          410511.24 367195.09,
          410533.95 367167.98,
          409747.77 367450.59,
          409177.19 367596.60,
          409169.80 367713.76,
          409079.41 367761.79,
          409093.04 367817.50,
          409207.30 368014.74,
          409272.68 368149.40,
          409154.81 368156.65,
          409177.97 368416.89,
          409297.11 368471.41,
          409302.81 368473.53,
          409295.06 368673.32,
          409240.68 368810.94,
          409439.13 368804.35,
          409201.18 369451.53
        ))',
        26191
      ),
      4326
    )
  )
  RETURNING id, geometry
)

INSERT INTO zones (
  id, zone_type_id, is_available,
  region_id, total_area, total_parcels, available_parcels, color, centroid
)
SELECT
  ins.id,
  1, -- zone privée
  TRUE,
  4, -- Rabat-Salé-Kénitra
  ST_Area(ins.geometry::geography)/10000.0, 10, 7, '#123456',
  ST_Centroid(ins.geometry)
FROM ins;

-- Ajouter une zone de démonstration (comme dans votre fichier original)
WITH ins AS (
  INSERT INTO spatial_entities (entity_type, name, description, geometry)
  VALUES (
    'zone', 'ZAINA', 'Zone générée automatiquement pour les tests',
    -- Conversion des coordonnées Lambert Nord Maroc (EPSG:26191) vers WGS84 (EPSG:4326)
    ST_Transform(
      ST_GeomFromText(
        'POLYGON((
          356080.37 362485.7,
          356300.3 362622.77,
          356362.67 362678.46,
          356382.85 362654.5,
          356488.42 362741.75,
          356414.57 362826.04,
          356652.88 362572.56,
          356402.7 362384.79,
          356205.35 362159.02,
          356069.83 362316.55,
          356056.8 362334.26,
          356051.06 362334.96,
          355943.48 362290.95,
          355924.29 362492.89,
          355931.72 362495.13,
          355940.2 362390.88,
          355947.7 362297.1,
          356063.49 362345.51,
          356074.42 362421.96,
          356082.49 362454.89,
          356080.37 362485.7
        ))',
        26191
      ),
      4326
    )
  )
  RETURNING id, geometry
)

INSERT INTO zones (
  id, zone_type_id, is_available,
  region_id, total_area, total_parcels, available_parcels, color, centroid
)
SELECT
  ins.id,
  1, -- zone privée
  TRUE,
  4, -- Rabat-Salé-Kénitra
  ST_Area(ins.geometry::geography)/10000.0, 10, 7, '#123456',
  ST_Centroid(ins.geometry)
FROM ins;

INSERT INTO zones (
  id, zone_type_id, is_available,
  region_id, total_area, total_parcels, available_parcels, color, centroid
)
SELECT
  ins.id,
  1, -- zone privée
  TRUE,
  4, -- Rabat-Salé-Kénitra
  ST_Area(ins.geometry::geography)/10000.0, 10, 7, '#123456',
  ST_Centroid(ins.geometry)
FROM ins;

-- Ajouter une zone de démonstration (comme dans votre fichier original)
WITH ins AS (
  INSERT INTO spatial_entities (entity_type, name, description, geometry)
  VALUES (
    'zone', 'OTTAWA', 'Zone générée automatiquement pour les tests',
    -- Conversion des coordonnées Lambert Nord Maroc (EPSG:26191) vers WGS84 (EPSG:4326)
    ST_Transform(
      ST_GeomFromText(
        'POLYGON((
          351900.19 363533.59,
          351989.68 363531.3,
          351988.73 363461.25,
          352188.64 363456.87,
          352187.55 363381.01,
          352384.73 363378.29,
          352381.99 363232.45,
          352287.38 363208.55,
          352241.53 363105.9,
          352244.52 363034.29,
          352303.18 362994.99,
          352241.33 362969.6,
          352074.35 362901.55,
          351963.88 362855.44,
          351980.16 362887.19,
          352030.09 363036.02,
          352045.39 363088.39,
          351909.06 363178.15,
          351931.83 363461.12,
          351900.19 363533.59
        ))',
        26191
      ),
      4326
    )
  )
  RETURNING id, geometry
)

INSERT INTO zones (
  id, zone_type_id, is_available,
  region_id, total_area, total_parcels, available_parcels, color, centroid
)
SELECT
  ins.id,
  1, -- zone privée
  TRUE,
  4, -- Rabat-Salé-Kénitra
  ST_Area(ins.geometry::geography)/10000.0, 10, 7, '#123456',
  ST_Centroid(ins.geometry)
FROM ins;

-- Message de fin
DO $$
BEGIN
  RAISE NOTICE '✅ Database initialization completed successfully!';
END $$;

