-- 1) Vider toutes les tables et réinitialiser les identifiants
TRUNCATE
  appointments,
  parcels,
  zones,
  spatial_entities,
  appointment_statuses,
  activities,
  amenities,
  roles,
  regions,
  zone_types,
  countries
RESTART IDENTITY CASCADE;

-- Pays
INSERT INTO countries (id, name, code)
VALUES (1, 'Maroc', 'MA')
ON CONFLICT DO NOTHING;

-- Types de zone
INSERT INTO zone_types (id, name) VALUES
  (1, 'privée'),
  (2, 'public')
ON CONFLICT DO NOTHING;

-- Régions
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

-- Rôles
INSERT INTO roles (id, name) VALUES
  (1, 'admin'),
  (2, 'manager'),
  (3, 'user')
ON CONFLICT DO NOTHING;

-- Commodités et activités
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

-- Statuts de rdv (notez le nom de table ending en -es)
INSERT INTO appointment_statuses (id, status_name) VALUES
  (1, 'Pending'),
  (2, 'Confirmed'),
  (3, 'Canceled')
ON CONFLICT DO NOTHING;

-- Zone principale
WITH ins AS (
  INSERT INTO spatial_entities (entity_type, name, description, geometry)
  VALUES (
    'zone', 'Zone A', 'Zone générée automatiquement',
    ST_GeomFromText(
      'POLYGON ((0.4285334177190453 30.48950764840616, 0.4287786284950915 30.48807211264298, 0.4290947544256785 30.486315588462812, 0.4296881519672345 30.48392584687679, 0.4297307796566536 30.483772802329703, 0.4304458863438128 30.48232109844186, 0.432291144896223 30.479777666400384, 0.4332215897328377 30.478714417899177, 0.4340740478508498 30.47787308943339, 0.4354864003925998 30.47655952134872, 0.4357207453155152 30.47632879242439, 0.4277670570674487 30.478618225016596, 0.422008677920454 30.47976600374899, 0.4219059199073505 30.480782211398868, 0.4209875694171799 30.481180309345973, 0.4211106546301572 30.481667152841236, 0.421795856538013 30.49588543551049, 0.422208482570505 30.48340479215854, 0.4228313629306511 30.48458844372715, 0.421647297382848 30.484626475371925, 0.4218159842509225 30.486892144551103, 0.4229977365499771 30.487390992780185, 0.423054394732626 30.48741061593454, 0.4229278401636991 30.489144617762054, 0.4223487098843758 30.490328666636888, 0.4243410377879032 30.49031340090962, 0.4263030294722804 30.49202562517024, 0.4276161550629616 30.48948861175795, 0.4285334177190453 30.48950764840616))',
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
  (SELECT id FROM zone_types WHERE name = 'privée'),
  TRUE,
  (SELECT id FROM regions WHERE name = 'Rabat-Salé-Kénitra'),
  ST_Area(ins.geometry::geography)/10000.0, 10, 7, '#123456',
  ST_Centroid(ins.geometry)
FROM ins;

-- Parcelles (cos et cus sont en pourcentage)
DO $$
DECLARE
  -- On récupère une fois pour toutes l'id de la zone 'Zone A'
  zone_id integer := (
    SELECT id
    FROM zones
    WHERE name = 'Zone A'
    LIMIT 1
  );
  -- Tableau de WKT pour les 10 parcelles
  coords text[] := ARRAY[
    'POLYGON ((0.4287334 30.4895076,0.4287334 30.4897076,0.4285334 30.4897076,0.4285334 30.4895076,0.4287334 30.4895076))',
    'POLYGON ((0.4289786 30.4880721,0.4289786 30.4882721,0.4287786 30.4882721,0.4287786 30.4880721,0.4289786 30.4880721))',
    'POLYGON ((0.4292948 30.4863156,0.4292948 30.4865156,0.4290948 30.4865156,0.4290948 30.4863156,0.4292948 30.4863156))',
    'POLYGON ((0.4298882 30.4839258,0.4298882 30.4841258,0.4296882 30.4841258,0.4296882 30.4839258,0.4298882 30.4839258))',
    'POLYGON ((0.4299308 30.4837728,0.4299308 30.4839728,0.4297308 30.4839728,0.4297308 30.4837728,0.4299308 30.4837728))',
    'POLYGON ((0.4306459 30.4823211,0.4306459 30.4825211,0.4304459 30.4825211,0.4304459 30.4823211,0.4306459 30.4823211))',
    'POLYGON ((0.4324911 30.4797777,0.4324911 30.4799777,0.4322911 30.4799777,0.4322911 30.4797777,0.4324911 30.4797777))',
    'POLYGON ((0.4334216 30.4787144,0.4334216 30.4789144,0.4332216 30.4789144,0.4332216 30.4787144,0.4334216 30.4787144))',
    'POLYGON ((0.4342740 30.4778731,0.4342740 30.4780731,0.4340740 30.4780731,0.4340740 30.4778731,0.4342740 30.4778731))',
    'POLYGON ((0.4356864 30.4765595,0.4356864 30.4767595,0.4354864 30.4767595,0.4354864 30.4765595,0.4356864 30.4765595))'
  ];
  -- Valeurs de CoS (en %)
  pct_vals numeric[] := ARRAY[0.47, 0.57, 0.46, 0.55, 0.75, 0.58, 0.53, 0.66, 0.75, 0.76];
  -- Valeurs de CuS (en %)
  cus_vals numeric[] := ARRAY[1.02, 0.96, 1.42, 1.48, 1.03, 0.94, 1.10, 1.44, 1.23, 1.09];
  i integer;
BEGIN
  FOR i IN 1..array_length(coords, 1) LOOP
    WITH ins AS (
      INSERT INTO spatial_entities (entity_type, name, description, geometry)
      VALUES (
        'parcel',
        format('Parcelle %s', i),
        'Auto-generated parcel',
        ST_GeomFromText(coords[i], 4326)
      )
      RETURNING id
    )
    INSERT INTO parcels (
      id,
      zone_id,
      area,
      is_free,
      is_available,
      is_showroom,
      "CoS",
      "CuS",
      photos
    )
    SELECT
      ins.id,
      zone_id,
      0.0,
      (i % 2 = 1),
      FALSE,
      FALSE,
      pct_vals[i],
      cus_vals[i],
      ARRAY[]::text[]
    FROM ins;
  END LOOP;
END
$$;

-- RDV
INSERT INTO appointments (
  id, parcel_id, appointment_status_id, requested_date,
  confirmed_date, appointment_message, contact_phone, company_name, job_title
)
VALUES
  (1,
   (SELECT id FROM parcels ORDER BY id LIMIT 1),
   (SELECT id FROM appointment_statuses WHERE status_name = 'Confirmed'),
   CURRENT_DATE, CURRENT_TIMESTAMP,
   'Demande de RDV', '+21261234560', 'Company0', 'Directeur'
  ),
  (2,
   (SELECT id FROM parcels ORDER BY id OFFSET 1 LIMIT 1),
   (SELECT id FROM appointment_statuses WHERE status_name = 'Pending'),
   CURRENT_DATE, CURRENT_TIMESTAMP,
   'Demande de RDV', '+21261234561', 'Company1', 'Directeur'
  ),
  (3,
   (SELECT id FROM parcels ORDER BY id OFFSET 2 LIMIT 1),
   (SELECT id FROM appointment_statuses WHERE status_name = 'Confirmed'),
   CURRENT_DATE, CURRENT_TIMESTAMP,
   'Demande de RDV', '+21261234562', 'Company2', 'Directeur'
  ),
  (4,
   (SELECT id FROM parcels ORDER BY id OFFSET 3 LIMIT 1),
   (SELECT id FROM appointment_statuses WHERE status_name = 'Pending'),
   CURRENT_DATE, CURRENT_TIMESTAMP,
   'Demande de RDV', '+21261234563', 'Company3', 'Directeur'
  ),
  (5,
   (SELECT id FROM parcels ORDER BY id OFFSET 4 LIMIT 1),
   (SELECT id FROM appointment_statuses WHERE status_name = 'Confirmed'),
   CURRENT_DATE, CURRENT_TIMESTAMP,
   'Demande de RDV', '+21261234564', 'Company4', 'Directeur'
  )
ON CONFLICT DO NOTHING;
