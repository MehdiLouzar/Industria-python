# Database Schema

This document describes the database tables and relationships implemented in the Flask application models located in `app/models`.

## SpatialEntity
Base table used for spatial objects. Other spatial models inherit from this table.

| Column         | Type       | Notes                    |
| -------------- | ---------- | ------------------------ |
| id             | Integer    | Primary key              |
| entity_type    | String     | Polymorphic identity     |
| name           | String     |                          |
| description    | Text       |                          |
| geometry       | Geometry   | Spatial column (WGS84). Accepts `lambert_coords` from the API which are converted on load. Provide any number of `x y` pairs as a JSON array or newline-separated string. The polygon is automatically closed if needed. |
| created_at     | Timestamp  | Defaults to `now()`      |

## Country

| Column | Type    | Notes       |
| ------ | ------- | ----------- |
| id     | Integer | Primary key |
| name   | String  |             |
| code   | String  |             |

## Region

| Column    | Type    | Notes                         |
| --------- | ------- | ----------------------------- |
| id        | Integer | Primary key                   |
| name      | String  |                               |
| country_id| Integer | Foreign key to `countries.id` |

## Role

| Column | Type    | Notes       |
| ------ | ------- | ----------- |
| id     | Integer | Primary key |
| name   | String  | Unique      |

## User

| Column           | Type      | Notes                              |
| ---------------- | --------- | ---------------------------------- |
| id               | Integer   | Primary key                        |
| first_name       | String    |                                    |
| last_name        | String    |                                    |
| email            | String    | Unique, required                   |
| provider         | String    | External provider                  |
| provider_id      | Text      |                                    |
| is_active        | Boolean   | Defaults to true                   |
| activation_token | Text      |                                    |
| user_role        | Integer   | Foreign key to `roles.id`          |
| created_at       | Timestamp | Defaults to `now()`                |

## Amenity

| Column        | Type    | Notes       |
| ------------- | ------- | ----------- |
| id            | Integer | Primary key |
| amenities_key | String  | Unique      |
| label         | String  |             |
| icon          | Text    |             |

## ZoneType

| Column | Type    | Notes       |
| ------ | ------- | ----------- |
| id     | Integer | Primary key |
| name   | String  | Unique      |

## Zone (inherits `SpatialEntity`)

| Column            | Type      | Notes                             |
| ----------------- | --------- | --------------------------------- |
| id                | Integer   | Primary key / FK to `spatial_entities.id` |
| zone_type_id      | Integer   | Foreign key to `zone_types.id`    |
| is_available      | Boolean   | Defaults to true                  |
| region_id         | Integer   | Foreign key to `regions.id`       |
| total_area        | Numeric   |                                   |
| total_parcels     | Integer   |                                   |
| available_parcels | Integer   |                                   |
| color             | String    |                                   |
| centroid          | Geometry  |                                   |

## Activity

| Column        | Type    | Notes       |
| ------------- | ------- | ----------- |
| id            | Integer | Primary key |
| activities_key| String  | Unique      |
| label         | String  |             |
| icon          | Text    |             |

## Parcel (inherits `SpatialEntity`)

| Column       | Type                         | Notes                                            |
| ------------ | ---------------------------- | ------------------------------------------------ |
| id           | Integer                      | Primary key / FK to `spatial_entities.id`        |
| zone_id      | Integer                      | Foreign key to `zones.id`                        |
| area         | Numeric                      |                                                  |
| is_free      | Boolean                      | Defaults to true                                 |
| is_available | Boolean                      | Defaults to true                                 |
| is_showroom  | Boolean                      | Defaults to false                                |
| CoS          | Numeric                      |                                                  |
| CuS          | Numeric                      |                                                  |
| photos       | Array(Text)                  |                                                  |

## ActivityLog

| Column   | Type      | Notes                              |
| -------- | --------- | ---------------------------------- |
| id       | Integer   | Primary key                        |
| user_id  | Integer   | Foreign key to `users.id`          |
| action   | Text      |                                    |
| target   | Text      |                                    |
| timestamp| Timestamp | Defaults to `now()`                |

## AppointmentStatus

| Column      | Type    | Notes       |
| ----------- | ------- | ----------- |
| id          | Integer | Primary key |
| status_name | String  |             |

## Appointment

| Column               | Type      | Notes                                        |
| -------------------- | --------- | -------------------------------------------- |
| id                   | Integer   | Primary key                                  |
| parcel_id            | Integer   | Foreign key to `parcels.id`                  |
| appointment_status_id| Integer   | Foreign key to `appointment_statuses.id`     |
| requested_date       | Date      |                                              |
| confirmed_date       | Timestamp |                                              |
| appointment_message  | Text      |                                              |
| contact_phone        | String    |                                              |
| company_name         | String    |                                              |
| job_title            | String    |                                              |
| created_at           | Timestamp | Defaults to `now()`                          |

## ZoneActivity (association table)

| Column     | Type    | Notes                                  |
| ---------- | ------- | -------------------------------------- |
| zone_id    | Integer | Primary key, FK to `zones.id`          |
| activity_id| Integer | Primary key, FK to `activities.id`     |

## ParcelAmenity (association table)

| Column    | Type    | Notes                                 |
| --------- | ------- | ------------------------------------- |
| parcel_id | Integer | Primary key, FK to `parcels.id`       |
| amenity_id| Integer | Primary key, FK to `amenities.id`     |

