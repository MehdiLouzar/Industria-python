-- cleanup_and_reset_fixed.sql

-- 1. Supprimer les zones en doublon (même county_code), ne garder que la plus petite id
DELETE FROM zones
 WHERE county_code = 'MA-RB'
   AND id NOT IN (
     SELECT MIN(id)
       FROM zones
      WHERE county_code = 'MA-RB'
      GROUP BY county_code
   );

-- 2. Récupérer l'id unique de la zone restante
WITH z AS (
  SELECT MIN(id) AS keep_id
    FROM zones
   WHERE county_code = 'MA-RB'
)
-- 3. Réaffecter toutes les parcelles vers cette zone
UPDATE parcels p
   SET zone_id = z.keep_id
  FROM z
 WHERE p.zone_id <> z.keep_id;

-- 4. Réinitialiser les séquences pour que les prochains INSERT repartent après le max(id)
--    Pour spatial_entities
SELECT setval(
  pg_get_serial_sequence('spatial_entities','id'),
  GREATEST((SELECT MAX(id) FROM spatial_entities), 1)
);

--    Pour zones
SELECT setval(
  pg_get_serial_sequence('zones','id'),
  GREATEST((SELECT MAX(id) FROM zones), 1)
);

--    Pour parcels
SELECT setval(
  pg_get_serial_sequence('parcels','id'),
  GREATEST((SELECT MAX(id) FROM parcels), 1)
);

--    Pour appointments
SELECT setval(
  pg_get_serial_sequence('appointments','id'),
  GREATEST((SELECT MAX(id) FROM appointments), 1)
);

-- 5. Vérification rapide
\\echo '=== Post-cleanup counts ==='
SELECT 'zones', count(*) FROM zones;
SELECT 'parcels', count(*) FROM parcels;
