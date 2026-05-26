class SimulationEngine:
    """Analytical core responsible for processing flight hazard metrics."""

    @staticmethod
    def run_hazard_simulation(origin: str, destination: str, layovers: list) -> dict:
        """
        Processes flight routing parameters to calculate mathematical risk scores.

        Args:
            origin (str): 3-letter code for departure.
            destination (str): 3-letter code for arrival.
            layovers (list): List of dictionaries containing transit airport data.
        """

        layovers_count = len(layovers)
        base_risk = 0.12  # False - Only to testing
        calculated_risk = base_risk + (layovers_count * 0.05)

        return {
            "origin_airport": origin.upper(),
            "destination_airport": destination.upper(),
            "total_layovers": layovers_count,
            "calculated_risk_factor": min(calculated_risk, 1.0) # Caps risk at 100%
        }






