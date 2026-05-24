-- AIRPORTS table
CREATE TABLE IF NOT EXISTS airports (
    airport_code VARCHAR(10) PRIMARY KEY,
    city_name VARCHAR(100),
    state_name VARCHAR(100)
);

-- AIRLINES table
CREATE TABLE IF NOT EXISTS airlines (
    carrier_code VARCHAR(10) PRIMARY KEY,
    airline_name VARCHAR(100)
);

-- FLIGHTS table
CREATE TABLE IF NOT EXISTS flights (
    flight_id SERIAL PRIMARY KEY,
    flight_date DATE,
    year INT,
    month INT,
    day_of_month INT,
    day_of_week INT,
    carrier VARCHAR(10) REFERENCES airlines (carrier_code),
    flight_num INT,
    origin VARCHAR(10) REFERENCES airports (airport_code),
    dest VARCHAR(10) REFERENCES airports (airport_code),
    crs_dep_time INT,
    dep_time FLOAT,
    dep_delay FLOAT DEFAULT 0.0,
    taxi_out FLOAT,
    wheels_off FLOAT,
    wheels_on FLOAT,
    taxi_in FLOAT,
    crs_arr_time INT,
    arr_time FLOAT,
    arr_delay FLOAT DEFAULT 0.0,
    cancelled BOOLEAN,
    cancellation_code VARCHAR(5),
    diverted BOOLEAN,
    distance FLOAT,
    carrier_delay FLOAT DEFAULT 0.0,
    weather_delay FLOAT DEFAULT 0.0,
    nas_delay FLOAT DEFAULT 0.0,
    security_delay FLOAT DEFAULT 0.0,
    late_aircraft_delay FLOAT DEFAULT 0.0
);

-- Indexes for heavy queries
CREATE INDEX IF NOT EXISTS idx_flights_origin_dest ON flights (origin, dest);

CREATE INDEX IF NOT EXISTS idx_flights_date ON flights (flight_date);

CREATE INDEX IF NOT EXISTS idx_flights_carrier ON flights (carrier);