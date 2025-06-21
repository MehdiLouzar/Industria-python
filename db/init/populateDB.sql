INSERT INTO countries (id, name, code) VALUES (1, 'Maroc', 'MA') ON CONFLICT DO NOTHING;

    INSERT INTO regions (id, name, country_id) 
    VALUES (1, 'Tanger-Tétouan-Al Hoceïma', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (2, 'L'Oriental', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (3, 'Fès-Meknès', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (4, 'Rabat-Salé-Kénitra', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (5, 'Béni Mellal-Khénifra', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (6, 'Casablanca-Settat', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (7, 'Marrakech-Safi', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (8, 'Drâa-Tafilalet', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (9, 'Souss-Massa', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (10, 'Guelmim-Oued Noun', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (11, 'Laâyoune-Sakia El Hamra', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO regions (id, name, country_id) 
    VALUES (12, 'Dakhla-Oued Ed-Dahab', 1)
    ON CONFLICT DO NOTHING;
    

    INSERT INTO roles (id, name)
    VALUES (1, 'admin')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO roles (id, name)
    VALUES (2, 'manager')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO roles (id, name)
    VALUES (3, 'user')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO users (
        id, first_name, last_name, email, password_hash,
        provider, provider_id, is_active, activation_token, user_role
    ) VALUES (
        1, 'User1', 'Test1', 'user1@example.com',
        'hashed_pwd', 'local', NULL, true, '', 
        (SELECT id FROM roles WHERE name = 'manager' LIMIT 1)
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO users (
        id, first_name, last_name, email, password_hash,
        provider, provider_id, is_active, activation_token, user_role
    ) VALUES (
        2, 'User2', 'Test2', 'user2@example.com',
        'hashed_pwd', 'local', NULL, true, '', 
        (SELECT id FROM roles WHERE name = 'user' LIMIT 1)
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO users (
        id, first_name, last_name, email, password_hash,
        provider, provider_id, is_active, activation_token, user_role
    ) VALUES (
        3, 'User3', 'Test3', 'user3@example.com',
        'hashed_pwd', 'local', NULL, true, '', 
        (SELECT id FROM roles WHERE name = 'user' LIMIT 1)
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO users (
        id, first_name, last_name, email, password_hash,
        provider, provider_id, is_active, activation_token, user_role
    ) VALUES (
        4, 'User4', 'Test4', 'user4@example.com',
        'hashed_pwd', 'local', NULL, true, '', 
        (SELECT id FROM roles WHERE name = 'manager' LIMIT 1)
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO users (
        id, first_name, last_name, email, password_hash,
        provider, provider_id, is_active, activation_token, user_role
    ) VALUES (
        5, 'User5', 'Test5', 'user5@example.com',
        'hashed_pwd', 'local', NULL, true, '', 
        (SELECT id FROM roles WHERE name = 'admin' LIMIT 1)
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO amenities (id, amenities_key, label, icon)
    VALUES (1, 'key_1', 'Amenity 1', 'icon-1')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO amenities (id, amenities_key, label, icon)
    VALUES (2, 'key_2', 'Amenity 2', 'icon-2')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO amenities (id, amenities_key, label, icon)
    VALUES (3, 'key_3', 'Amenity 3', 'icon-3')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO amenities (id, amenities_key, label, icon)
    VALUES (4, 'key_4', 'Amenity 4', 'icon-4')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO amenities (id, amenities_key, label, icon)
    VALUES (5, 'key_5', 'Amenity 5', 'icon-5')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO activities (id, activities_key, label, icon)
    VALUES (1, 'key_1', 'Activity 1', 'icon-1')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO activities (id, activities_key, label, icon)
    VALUES (2, 'key_2', 'Activity 2', 'icon-2')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO activities (id, activities_key, label, icon)
    VALUES (3, 'key_3', 'Activity 3', 'icon-3')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO activities (id, activities_key, label, icon)
    VALUES (4, 'key_4', 'Activity 4', 'icon-4')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO activities (id, activities_key, label, icon)
    VALUES (5, 'key_5', 'Activity 5', 'icon-5')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO appointment_status (id, status_name)
    VALUES (1, 'Pending')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO appointment_status (id, status_name)
    VALUES (2, 'Confirmed')
    ON CONFLICT DO NOTHING;
    

    INSERT INTO appointment_status (id, status_name)
    VALUES (3, 'Canceled')
    ON CONFLICT DO NOTHING;
    

WITH ins AS (
    INSERT INTO spatial_entities (entity_type, name, description, geometry)
    VALUES ('zone', 'Zone A', 'Zone générée automatiquement', ST_GeomFromText('POLYGON ((0.4285334177190453 30.48950764840616, 0.4287786284950915 30.48807211264298, 0.4290947544256785 30.486315588462812, 0.4296881519672345 30.48392584687679, 0.4297307796566536 30.483772802329703, 0.4304458863438128 30.48232109844186, 0.432291144896223 30.479777666400384, 0.4332215897328377 30.478714417899177, 0.4340740478508498 30.47787308943339, 0.4354864003925998 30.47655952134872, 0.4357207453155152 30.47632879242439, 0.4277670570674487 30.478618225016596, 0.422008677920454 30.47976600374899, 0.4219059199073505 30.480782211398868, 0.4209875694171799 30.481180309345973, 0.4211106546301572 30.481667152841236, 0.421795856538013 30.49588543551049, 0.422208482570505 30.48340479215854, 0.4228313629306511 30.48458844372715, 0.421647297382848 30.484626475371925, 0.4218159842509225 30.486892144551103, 0.4229977365499771 30.487390992780185, 0.423054394732626 30.48741061593454, 0.4229278401636991 30.489144617762054, 0.4223487098843758 30.490328666636888, 0.4243410377879032 30.49031340090962, 0.4263030294722804 30.49202562517024, 0.4276161550629616 30.48948861175795, 0.4285334177190453 30.48950764840616))', 4326))
    RETURNING id, geometry
)
INSERT INTO zones (
    id, county_code, zone_type, zone_description, is_available,
    region_id, total_area, total_parcels, available_parcels, color, centroid
)
SELECT
    ins.id, 'MA-RB', 1, 'Zone test', true,
    (SELECT id FROM regions WHERE name = 'Rabat-Salé-Kénitra'),
    ST_Area(ins.geometry::geography) / 10000.0, 10, 7, '#123456', ST_Centroid(ins.geometry)
FROM ins;


    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 1', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4287334177190453 30.48950764840616, 0.4287334177190453 30.48970764840616, 0.4285334177190453 30.48970764840616, 0.4285334177190453 30.48950764840616, 0.4287334177190453 30.48950764840616))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, false,
        false, 0.47, 1.02, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 2', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4289786284950915 30.48807211264298, 0.4289786284950915 30.488272112642978, 0.4287786284950915 30.488272112642978, 0.4287786284950915 30.48807211264298, 0.4289786284950915 30.48807211264298))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, false, false,
        false, 0.57, 0.96, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 3', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4292947544256784 30.486315588462812, 0.4292947544256784 30.48651558846281, 0.4290947544256785 30.48651558846281, 0.4290947544256785 30.486315588462812, 0.4292947544256784 30.486315588462812))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, false, true,
        false, 0.46, 1.42, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 4', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4298881519672345 30.48392584687679, 0.4298881519672345 30.48412584687679, 0.4296881519672345 30.48412584687679, 0.4296881519672345 30.48392584687679, 0.4298881519672345 30.48392584687679))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, false,
        false, 0.55, 1.48, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 5', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4299307796566536 30.483772802329703, 0.4299307796566536 30.483972802329703, 0.4297307796566536 30.483972802329703, 0.4297307796566536 30.483772802329703, 0.4299307796566536 30.483772802329703))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, true,
        false, 0.75, 1.03, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 6', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4306458863438127 30.48232109844186, 0.4306458863438127 30.48252109844186, 0.4304458863438128 30.48252109844186, 0.4304458863438128 30.48232109844186, 0.4306458863438127 30.48232109844186))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, false,
        false, 0.58, 0.94, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 7', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.432491144896223 30.479777666400384, 0.432491144896223 30.479977666400384, 0.432291144896223 30.479977666400384, 0.432291144896223 30.479777666400384, 0.432491144896223 30.479777666400384))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, true,
        false, 0.53, 1.1, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 8', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4334215897328377 30.478714417899177, 0.4334215897328377 30.478914417899176, 0.4332215897328377 30.478914417899176, 0.4332215897328377 30.478714417899177, 0.4334215897328377 30.478714417899177))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, false, true,
        false, 0.66, 1.44, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 9', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4342740478508498 30.47787308943339, 0.4342740478508498 30.47807308943339, 0.4340740478508498 30.47807308943339, 0.4340740478508498 30.47787308943339, 0.4342740478508498 30.47787308943339))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, false,
        false, 0.75, 1.23, ARRAY[]::text[]
    FROM ins;
    

    WITH ins AS (
        INSERT INTO spatial_entities (entity_type, name, description, geometry)
        VALUES ('parcel', 'Parcelle 10', 'Auto-generated parcel', ST_GeomFromText('POLYGON ((0.4356864003925998 30.47655952134872, 0.4356864003925998 30.47675952134872, 0.4354864003925998 30.47675952134872, 0.4354864003925998 30.47655952134872, 0.4356864003925998 30.47655952134872))', 4326))
        RETURNING id
    )
    INSERT INTO parcels (
        id, zone_id, area, is_free, is_available, is_showroom, cos, cus, photos
    )
    SELECT
        ins.id,
        (SELECT id FROM zones WHERE county_code = 'MA-RB'),
        0.0, true, false,
        false, 0.76, 1.09, ARRAY[]::text[]
    FROM ins;
    

    INSERT INTO appointments (
        id, user_id, parcel_id, appointment_status_id, requested_date,
        confirmed_date, appointment_message, contact_phone, company_name, job_title
    )
    VALUES (
        1,
        (SELECT id FROM users WHERE email = 'user1@example.com'),
        (SELECT id FROM parcels WHERE id = (SELECT MIN(id) FROM parcels) + 0),
        (SELECT id FROM appointment_status WHERE status_name = 'Confirmed'),
        CURRENT_DATE, CURRENT_TIMESTAMP,
        'Demande de RDV', '+21261234560',
        'Company0', 'Directeur'
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO appointments (
        id, user_id, parcel_id, appointment_status_id, requested_date,
        confirmed_date, appointment_message, contact_phone, company_name, job_title
    )
    VALUES (
        2,
        (SELECT id FROM users WHERE email = 'user2@example.com'),
        (SELECT id FROM parcels WHERE id = (SELECT MIN(id) FROM parcels) + 1),
        (SELECT id FROM appointment_status WHERE status_name = 'Pending'),
        CURRENT_DATE, CURRENT_TIMESTAMP,
        'Demande de RDV', '+21261234561',
        'Company1', 'Directeur'
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO appointments (
        id, user_id, parcel_id, appointment_status_id, requested_date,
        confirmed_date, appointment_message, contact_phone, company_name, job_title
    )
    VALUES (
        3,
        (SELECT id FROM users WHERE email = 'user3@example.com'),
        (SELECT id FROM parcels WHERE id = (SELECT MIN(id) FROM parcels) + 2),
        (SELECT id FROM appointment_status WHERE status_name = 'Confirmed'),
        CURRENT_DATE, CURRENT_TIMESTAMP,
        'Demande de RDV', '+21261234562',
        'Company2', 'Directeur'
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO appointments (
        id, user_id, parcel_id, appointment_status_id, requested_date,
        confirmed_date, appointment_message, contact_phone, company_name, job_title
    )
    VALUES (
        4,
        (SELECT id FROM users WHERE email = 'user4@example.com'),
        (SELECT id FROM parcels WHERE id = (SELECT MIN(id) FROM parcels) + 3),
        (SELECT id FROM appointment_status WHERE status_name = 'Pending'),
        CURRENT_DATE, CURRENT_TIMESTAMP,
        'Demande de RDV', '+21261234563',
        'Company3', 'Directeur'
    ) ON CONFLICT DO NOTHING;
    

    INSERT INTO appointments (
        id, user_id, parcel_id, appointment_status_id, requested_date,
        confirmed_date, appointment_message, contact_phone, company_name, job_title
    )
    VALUES (
        5,
        (SELECT id FROM users WHERE email = 'user5@example.com'),
        (SELECT id FROM parcels WHERE id = (SELECT MIN(id) FROM parcels) + 4),
        (SELECT id FROM appointment_status WHERE status_name = 'Confirmed'),
        CURRENT_DATE, CURRENT_TIMESTAMP,
        'Demande de RDV', '+21261234564',
        'Company4', 'Directeur'
    ) ON CONFLICT DO NOTHING;
    