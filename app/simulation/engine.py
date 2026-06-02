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
            return pd.DataFrame()  # Alternative solution to avoid API crash

    @staticmethod
    def run_hazard_simulation(origin: str, destination: str, layovers: list) -> dict:
        """
        Processes flight routing parameters to calculate mathematical risk scores.

        Args:
            origin (str): 3-letter code for departure.
            destination (str): 3-letter code for arrival.
            layovers (list): List of dictionaries containing transit airport data.
        """
        # Generate the list of airports
        stops = [origin.upper()]
        for layover in layovers:
            # Extract the airport code
            layover_code = layover.get("airport")
            if layover_code:
                stops.append(layover_code.upper())
        stops.append(destination.upper())

        # Initializing metrics
        total_segments = len(stops) - 1
        analyzed_segments_count = 0
        sum_delay_probabilities = 0.0
        sum_average_delays = 0.0
        combined_sample_size = 0

        # Pair element i with element i+1 to evaluate every single flight
        for i in range(total_segments):
            seg_origin = stops[i]
            seg_dest = stops[i + 1]

            # Fetch historical data from PostgreSQL for this specific segment
            df_segment = SimulationEngine._get_historical_data(seg_origin, seg_dest)

            # Safeguard: If a segment has no historical records, I omit it to avoid errors in the calculations
            if df_segment.empty:
                continue

            # Increment the route segment counter
            analyzed_segments_count += 1

            # Calculate the current segment
            segment_total_flights = len(df_segment)
            segment_delayed_flights = df_segment[df_segment["dep_delay"] > 15]

            segment_prob_delay = (
                len(segment_delayed_flights) / segment_total_flights
                if segment_total_flights > 0
                else 0.0
            )
            segment_mean_delay = df_segment["dep_delay"].mean()

            if pd.isna(segment_mean_delay):
                segment_mean_delay = 0.0

            # Collect metrics across all historical flight records
            combined_sample_size += segment_total_flights
            sum_delay_probabilities += segment_prob_delay
            sum_average_delays += segment_mean_delay

        # If no segments could be analyzed, trigger fallback
        if analyzed_segments_count == 0:
            return {
                "origin_airport": origin.upper(),
                "destination_airport": destination.upper(),
                "total_layovers": len(layovers),
                "calculated_risk_factor": 0.0,
                "status": "insufficient_historical_data",
            }

        # Calculate final metrics, sum of probabilities capped at 1.0
        final_risk_factor = min(sum_delay_probabilities, 1.0)
        global_average_delay = sum_average_delays / analyzed_segments_count

        return {
            "origin_airport": origin.upper(),
            "destination_airport": destination.upper(),
            "total_layovers": len(layovers),
            "metrics": {
                "historical_sample_size": combined_sample_size,
                "base_delay_probability": round(
                    sum_delay_probabilities / analyzed_segments_count, 4
                ),
                "average_departure_delay_minutes": round(global_average_delay, 2),
            },
            "calculated_risk_factor": round(final_risk_factor, 4),
            "status": "calculated",
        }
