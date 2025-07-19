-- db/init/initDB.sql
-- Reset the database and populate demo data for Industria

-- Create extension for PostGIS if not exists
CREATE EXTENSION IF NOT EXISTS postgis;

-- Drop and recreate schema cleanly
DO
$$
DECLARE
  tbl text;
  tables text[] := ARRAY[
    'zone_activities','parcel_amenities','appointments','parcels',
    'zones','zone_types','activities','amenities',
    'appointment_status','regions','countries',
    'activity_logs','spatial_entities'
  ];
BEGIN
  -- Supprimer les tables dans l'ordre pour éviter les contraintes FK
  FOREACH tbl IN ARRAY tables LOOP
    IF to_regclass('public.' || tbl) IS NOT NULL THEN
      EXECUTE format('TRUNCATE TABLE public.%I RESTART IDENTITY CASCADE', tbl);
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
  (1, 'key_1', 'Amenity 1', 'icon-1'),
  (2, 'key_2', 'Amenity 2', 'icon-2'),
  (3, 'key_3', 'Amenity 3', 'icon-3'),
  (4, 'key_4', 'Amenity 4', 'icon-4'),
  (5, 'key_5', 'Amenity 5', 'icon-5')
ON CONFLICT (id) DO NOTHING;

INSERT INTO activities (id, activities_key, label, icon) VALUES
  (1, 'key_1', 'Activity 1', 'icon-1'),
  (2, 'key_2', 'Activity 2', 'icon-2'),
  (3, 'key_3', 'Activity 3', 'icon-3'),
  (4, 'key_4', 'Activity 4', 'icon-4'),
  (5, 'key_5', 'Activity 5', 'icon-5')
ON CONFLICT (id) DO NOTHING;

INSERT INTO appointment_status (id, status_name) VALUES
  (1, 'Pending'),
  (2, 'Confirmed'), 
  (3, 'Canceled')
ON CONFLICT (id) DO NOTHING;

-- Ajouter une zone de démonstration (comme dans votre fichier original)
WITH ins AS (
  INSERT INTO spatial_entities (entity_type, name, description, geometry)
  VALUES (
    'zone', 'Zone de Démonstration', 'Zone générée automatiquement pour les tests',
    ST_Transform(
      ST_GeomFromText(
        'POLYGON ((0.4285334177190453 30.48950764840616, 0.4287786284950915 30.48807211264298, 0.4290947544256785 30.486315588462812, 0.4296881519672345 30.48392584687679, 0.4297307796566536 30.483772802329703, 0.4304458863438128 30.48232109844186, 0.432291144896223 30.479777666400384, 0.4332215897328377 30.478714417899177, 0.4340740478508498 30.47787308943339, 0.4354864003925998 30.47655952134872, 0.4357207453155152 30.47632879242439, 0.4277670570674487 30.478618225016596, 0.422008677920454 30.47976600374899, 0.4219059199073505 30.480782211398868, 0.4209875694171799 30.481180309345973, 0.4211106546301572 30.481667152841236, 0.421795856538013 30.49588543551049, 0.422208482570505 30.48340479215854, 0.4228313629306511 30.48458844372715, 0.421647297382848 30.484626475371925, 0.4218159842509225 30.486892144551103, 0.4229977365499771 30.487390992780185, 0.423054394732626 30.48741061593454, 0.4229278401636991 30.489144617762054, 0.4223487098843758 30.490328666636888, 0.4243410377879032 30.49031340090962, 0.4263030294722804 30.49202562517024, 0.4276161550629616 30.48948861175795, 0.4285334177190453 30.48950764840616))',
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