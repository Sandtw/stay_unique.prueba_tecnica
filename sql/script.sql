CREATE DATABASE IF NOT EXISTS BD_STAY_UNIQUE;
USE BD_STAY_UNIQUE;

CREATE TABLE IF NOT EXISTS properties_owner (
    property_id BIGINT PRIMARY KEY,
    capacity INT,
    square_mts FLOAT,
    property_type VARCHAR(50),
    n_bedrooms SMALLINT
);


CREATE TABLE IF NOT EXISTS properties_competitor (
    property_id BIGINT PRIMARY KEY,
    property_name VARCHAR(200),
    reference_rate_night FLOAT,
    rating DECIMAL(4, 2),
    n_reviews INT,
    city VARCHAR(100),
    country VARCHAR(50),
    property_type VARCHAR(50),
    url_property TEXT
);

CREATE TABLE booking (
    booking_id INT PRIMARY KEY,
    created_date VARCHAR(30),
    check_in_date VARCHAR(30),
    check_out_date VARCHAR(30),
    n_nights DOUBLE,
    n_adults INT,
    n_children INT,
    n_infants INT,
    total_without_extras DOUBLE,
    avg_rate_night DOUBLE,
    channel VARCHAR(100),
    total_paid FLOAT,
    property_id BIGINT,
    CONSTRAINT fk_prop FOREIGN KEY (property_id) REFERENCES properties_owner(property_id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);

SELECT * FROM properties_owner;
SELECT * FROM properties_competitor;
SELECT * FROM booking;