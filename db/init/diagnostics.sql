-- diagnostics.sql

-- 1. Afficher un titre pour les comptages
\echo '=== Comptages des tables ==='

-- 2. Comptage des lignes de chaque table
SELECT 'countries'            AS table_name, count(*) FROM countries;
SELECT 'regions'              AS table_name, count(*) FROM regions;
SELECT 'roles'                AS table_name, count(*) FROM roles;
SELECT 'amenities'            AS table_name, count(*) FROM amenities;
SELECT 'activities'           AS table_name, count(*) FROM activities;
SELECT 'appointment_statuses' AS table_name, count(*) FROM appointment_statuses;
SELECT 'zones'                AS table_name, count(*) FROM zones;
SELECT 'parcels'              AS table_name, count(*) FROM parcels;
SELECT 'appointments'         AS table_name, count(*) FROM appointments;

-- 3. Lister quelques lignes clés pour vérification
\echo '=== Aperçu des données (LIMIT 5) ==='

SELECT * FROM countries            LIMIT 5;
SELECT * FROM regions              LIMIT 5;
SELECT * FROM zones                LIMIT 5;
SELECT * FROM parcels              LIMIT 5;
SELECT * FROM appointments         LIMIT 5;

-- 4. Exemple d’isolation pour la table zones
--    (décommentez pour tester l’insertion seule et voir l’erreur)
-- WITH ins AS (
--   INSERT INTO spatial_entities (entity_type,name,description,geometry)
--   VALUES (
--     'zone','Zone A','Zone test',
--     ST_MakeEnvelope(0.42,30.48,0.44,30.50,4326)
--   )
--   RETURNING id, geometry
-- )
-- INSERT INTO zones (zone_type_id, region_id, total_area)
-- SELECT
--   (SELECT id FROM zone_types WHERE name = 'privée'),
--   (SELECT id FROM regions WHERE name = 'Rabat-Salé-Kénitra'),
--   ST_Area(geometry::geography)/10000.0
-- FROM ins;

-- 5. Note : pour tester sans ON CONFLICT, commentez les clause ON CONFLICT de votre script original.
