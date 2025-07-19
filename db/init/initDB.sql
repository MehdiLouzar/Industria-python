-- db/init/initDB.sql
-- Reset the database and populate demo data for Industria
-- Placeholder for database initialization scripts
-- Create extension for PostGIS if not exists
CREATE EXTENSION IF NOT EXISTS postgis;
DO
$$
DECLARE
  tbl text;
  tables text[] := ARRAY[
    'zone_activities','parcel_amenities','appointments','parcels',
    'zones','zone_types','activities','amenities',
    'appointment_status','regions','countries','roles',
    'users','activity_logs','spatial_entities'
  ];
BEGIN
  FOREACH tbl IN ARRAY tables LOOP
    IF to_regclass('public.' || tbl) IS NOT NULL THEN
      EXECUTE format(
        'TRUNCATE TABLE public.%I RESTART IDENTITY CASCADE',
        tbl
      );
    END IF;
  END LOOP;
END
$$;

-- Basic reference data
INSERT INTO countries (id, name, code) VALUES
  (1, 'Maroc', 'MA')
ON CONFLICT DO NOTHING;

INSERT INTO zone_types (id, name) VALUES
  (1, 'privée'),
  (2, 'public')
ON CONFLICT DO NOTHING;

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
ON CONFLICT DO NOTHING;

INSERT INTO roles (id, name) VALUES
  (1, 'admin'),
  (2, 'manager'),
  (3, 'user')
ON CONFLICT DO NOTHING;

INSERT INTO amenities (id, amenities_key, label, icon) VALUES
  (1, 'key_1', 'Amenity 1', 'icon-1'),
  (2, 'key_2', 'Amenity 2', 'icon-2'),
  (3, 'key_3', 'Amenity 3', 'icon-3'),
  (4, 'key_4', 'Amenity 4', 'icon-4'),
  (5, 'key_5', 'Amenity 5', 'icon-5')
ON CONFLICT DO NOTHING;

INSERT INTO activities (id, activities_key, label, icon) VALUES
  (1, 'key_1', 'Activity 1', 'icon-1'),
  (2, 'key_2', 'Activity 2', 'icon-2'),
  (3, 'key_3', 'Activity 3', 'icon-3'),
  (4, 'key_4', 'Activity 4', 'icon-4'),
  (5, 'key_5', 'Activity 5', 'icon-5')
ON CONFLICT DO NOTHING;

INSERT INTO appointment_status (id, status_name) VALUES
  (1, 'Pending'),
  (2, 'Confirmed'),
  (3, 'Canceled')
ON CONFLICT DO NOTHING;