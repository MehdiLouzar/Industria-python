-- Upgrade existing database to support zone types
-- Adds zone_types table and converts zones.zone_type to zone_type_id
CREATE TABLE IF NOT EXISTS zone_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);

INSERT INTO zone_types (id, name) VALUES
    (1, 'privée'),
    (2, 'public')
ON CONFLICT DO NOTHING;

-- Rename old column if present
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='zones' AND column_name='zone_type'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='zones' AND column_name='zone_type_id'
    ) THEN
        ALTER TABLE zones RENAME COLUMN zone_type TO zone_type_id;
    END IF;
END$$;

ALTER TABLE zones
    ADD COLUMN IF NOT EXISTS zone_type_id INTEGER;

ALTER TABLE zones DROP COLUMN IF EXISTS zone_description;

ALTER TABLE zones DROP COLUMN IF EXISTS county_code;

ALTER TABLE zones
    ADD CONSTRAINT IF NOT EXISTS zones_zone_type_id_fkey
    FOREIGN KEY (zone_type_id) REFERENCES zone_types(id);

