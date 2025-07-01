# Furai API

[![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?logo=swagger&logoColor=white)](https://api.furai-jdm.com/) [![codecov](https://codecov.io/github/brdtheo/furai-api/graph/badge.svg?token=NM2K67CRBH)](https://codecov.io/github/brdtheo/furai-api)

This is the REST API for [Furai car rental](https://github.com/brdtheo/furai) built with Django Rest Framework

## Database schema

The database models are relatively simple. We have cars, customers and each customer can create a booking from a car. A customer is always related to a user for authentication purposes.

```mermaid
erDiagram
    car {
        int id PK
        string make
        string model
        string slug UK
        int capacity
        string transmission "car_transmission: manual | automatic"
        string drivetrain "car_drivetrain: FWD, RWD, AWD, 4WD"
        string fuel_type "fuel_type: gasohol_e85, gasohol_e20, gasohol_91, gasohol_95, bensin, premium_bensin"
        float fuel_consumption_metric
        string engine_code
        int power_hp
        int power_max_rpm
        int price_hourly_cents
        int price_9_hours_cents
        int price_12_hours_cents
        int price_24_hours_cents
        timestamptz created_at "default: now()"
    }
    car_media {
        int id PK
        string url UK
        bool is_thumbnail
        int car_id FK
        timestamptz created_at "default: now()"
    }
    car_feature {
        int id PK
        string name
    }
    car_feature_assigment {
        int id PK
        int car_feature_id FK
        int car_id FK
    }
    booking {
        int id PK
        int car_id FK
        int customer_id FK
        timestamp start_date
        timestamp end_date
        string status "booking_status: complete, cancelled_by_customer, cancelled_by_staff"
        int price_cts
        timestamptz created_at "default: now()"
    }
    customer {
        int id PK
        string stripe_id
        int user_id FK
        string first_name
        string last_name
        string address_line1
        string address_line2
        string address_city
        int address_postal_code
        string address_state
        string address_country
        int passport UK
        string phone UK
        timestamptz created_at "default: now()"
    }
    user {
        int id PK
        string email UK
        timestamptz created_at "default: now()"
        string role "user_role: customer, staff"
    }

    %% Relationships
    car ||--o{ car_media : "has media"
    car ||--o{ car_feature_assigment : "has features assigned"
    car_feature ||--o{ car_feature_assigment : "is assigned to"
    car ||--o{ booking : "booked in"
    customer ||--o{ booking : "makes"
    customer }o--|| user : "is (linked user)"

    %% ENUMS as comments for reference
    %% fuel_type: gasohol_e85, gasohol_e20, gasohol_91, gasohol_95, bensin, premium_bensin
    %% car_transmission: manual, automatic
    %% car_drivetrain: front_wheel_drive, rear_wheel_drive, all_wheel_drive, four_wheel_drive
    %% booking_status: complete, cancelled_by_customer, cancelled_by_staff
    %% user_role: customer, staff
```
