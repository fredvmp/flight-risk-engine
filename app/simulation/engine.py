import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


class SimulationEngine:
    """Analytical core responsible for processing flight hazard metrics."""

    @staticmethod
    def _get_historical_data(origin: str, destination: str) -> pd.DataFrame:
        """
        Method to extract historical flight subsets from PostgreSQL.
        An empty DataFrame is returned if a database connection error occurs.
        """

        query = """
            SELECT dep_delay, arr_delay, weather_delay, nas_delay, late_aircraft_delay, cancelled
            FROM flights
            WHERE origin = :origin AND dest = :destination           
        """

        try:
            from app.database import db

            # Run the query and add the result to a DataFrame
            df = pd.read_sql_query(
                sql=text(query),
                con=db.engine,
                params={"origin": origin, "destination": destination},
            )
            return df

        except SQLAlchemyError as e:
            print(
                f"[ENGINE DATABASE ERROR]: Failed to fetch history for {origin}->{destination}. Details: {str(e)}"
            )
            return pd.DataFrame()  # Graceful fallback to avoid API crash

    @staticmethod
    def run_hazard_simulation(origin: str, destination: str, layovers: list) -> dict:
        """
        Processes flight routing parameters to calculate mathematical risk scores.

        Args:
            origin (str): 3-letter code for departure.
            destination (str): 3-letter code for arrival.
            layovers (list): List of dictionaries containing transit airport data.
        """
        # Fetch historical analytics
        df = SimulationEngine._get_historical_data(origin, destination)

        # Early validation (Fail-Fast)
        if df.empty:
            return {
                "origin_airport": origin.upper(),
                "destination_airport": destination.upper(),
                "total_layovers": len(layovers),
                "calculated_risk_factor": 0.0,
                "status": "insufficient_historical_data",
            }

        # PANDAS - Analytical Core
        total_flights = len(df)

        delayed_flights = df[df["dep_delay"] > 15]

        prob_delay = len(delayed_flights) / total_flights if total_flights > 0 else 0.0

        # Calculate Mean Delay ignoring NaNs
        mean_delay = df["dep_delay"].mean()
        if pd.isna(mean_delay):
            mean_delay = 0.0

        # Adjust risk score dynamically if the user specified layovers
        layovers_count = len(layovers)
        final_risk_factor = prob_delay + (layovers_count * 0.10)

        return {
            "origin_airport": origin.upper(),
            "destination_airport": destination.upper(),
            "total_layovers": layovers_count,
            "metrics": {
                "historical_sample_size": total_flights,
                "base_delay_probability": round(prob_delay, 4),
                "average_departure_delay_minutes": round(mean_delay, 2),
            },
            "calculated_risk_factor": min(round(final_risk_factor, 4), 1.0),
            "status": "calculated",
        }
