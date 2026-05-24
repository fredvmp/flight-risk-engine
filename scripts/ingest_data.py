import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables for database connection
load_dotenv()

# Database credentials configuration
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "flight_risk_db")

# Create SQLAlchemy database engine
DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

CSV_PATH = "data/flight_data_2024.csv"


def ingest_data():
    print("Starting data ingestion.")

    if not os.path.exists(CSV_PATH):
        print(
            f"Error: CSV file not found at {CSV_PATH}. Please verify the location.")
        return

    # =================================================
    # Read the CSV file
    # =================================================
    print("Reading CSV file...")
    df = pd.read_csv(CSV_PATH)
    print(f"CSV loaded successfully. Total rows to process: {len(df):,}")

    # Remove whitespaces
    df.columns = df.columns.str.strip()

    # =================================================
    # Populate AIRPORTS table
    # =================================================

    # Extract unique origin airports
    df_orig = df[['origin', 'origin_city_name', 'origin_state_nm']].copy()
    df_orig.columns = ['airport_code', 'city_name', 'state_name']

    # Extract unique destination airports
    df_dest = df[['dest', 'dest_city_name', 'dest_state_nm']].copy()
    df_dest.columns = ['airport_code', 'city_name', 'state_name']

    # Merge both sources into a single list
    df_airports = pd.concat([df_orig, df_dest], ignore_index=True).drop_duplicates(
        subset=['airport_code'])

    # Append records to the existing database table
    df_airports.to_sql('airports', engine, if_exists='append', index=False)
    print(f"Inserted {len(df_airports)} unique airports.")

    # =================================================
    # Populate AIRLINES table
    # =================================================

    # Extract unique carrier codes
    unique_carriers = df['op_unique_carrier'].unique()
    df_airlines = pd.DataFrame({
        'carrier_code': unique_carriers,
        'airline_name': unique_carriers  # Temporary name
    })

    df_airlines.to_sql('airlines', engine, if_exists='append', index=False)
    print(f"Inserted {len(df_airlines)} unique airlines.")

    # =================================================
    # Populate FLIGHTS table
    # =================================================

    # Select and map source columns to match schema requirements
    df_flights = df[[
        'fl_date', 'year', 'month', 'day_of_month', 'day_of_week',
        'op_unique_carrier', 'op_carrier_fl_num', 'origin', 'dest',
        'crs_dep_time', 'dep_time', 'dep_delay', 'taxi_out', 'wheels_off',
        'wheels_on', 'taxi_in', 'crs_arr_time', 'arr_time', 'arr_delay',
        'cancelled', 'cancellation_code', 'diverted', 'distance',
        'carrier_delay', 'weather_delay', 'nas_delay', 'security_delay',
        'late_aircraft_delay'
    ]].copy()

    df_flights.columns = [
        'flight_date', 'year', 'month', 'day_of_month', 'day_of_week',
        'carrier', 'flight_num', 'origin', 'dest',
        'crs_dep_time', 'dep_time', 'dep_delay', 'taxi_out', 'wheels_off',
        'wheels_on', 'taxi_in', 'crs_arr_time', 'arr_time', 'arr_delay',
        'cancelled', 'cancellation_code', 'diverted', 'distance',
        'carrier_delay', 'weather_delay', 'nas_delay', 'security_delay',
        'late_aircraft_delay'
    ]

    # Convert flags to boolean types for PostgreSQL
    df_flights['cancelled'] = df_flights['cancelled'].astype(bool)
    df_flights['diverted'] = df_flights['diverted'].astype(bool)

    # Convert strings/dates to standard pandas datetime objects
    df_flights['flight_date'] = pd.to_datetime(
        df_flights['flight_date']).dt.date

    # Stream data in chunks for memory safety and optimized throughput
    df_flights.to_sql('flights', engine, if_exists='append',
                      index=False, chunksize=50000)

    print("Data ingestion completed successfully!")


if __name__ == "__main__":
    ingest_data()
