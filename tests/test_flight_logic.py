import pytest
import pandas as pd
from unittest.mock import patch
from app.simulation.engine import SimulationEngine


@pytest.fixture
def mock_direct_flight_data():
    """Provides a controlled DataFrame representing a direct flight history slice.

    Total: 4 flights. Delayed (>15 min): 2 flights (20, 30).
    Probability: 2/4 = 0.5. Mean delay: (0+10+20+30)/4 = 15.0.
    """
    return pd.DataFrame(
        {
            "dep_delay": [0, 10, 20, 30],
            "arr_delay": [0, 5, 25, 35],
            "weather_delay": [0, 0, 0, 0],
            "nas_delay": [0, 0, 0, 0],
            "late_aircraft_delay": [0, 0, 0, 0],
            "cancelled": [False, False, False, False],
        }
    )


@pytest.fixture
def mock_segment_1_data():
    """Provides historical data for Leg 1 (e.g., LAX -> ORD).

    Total: 2 flights. Delayed: 1 (20). Prob: 0.5. Mean: 10.0.
    """
    return pd.DataFrame({"dep_delay": [0, 20]})


@pytest.fixture
def mock_segment_2_data():
    """Provides historical data for Leg 2 (e.g., ORD -> JFK).

    Total: 2 flights. Delayed: 1 (30). Prob: 0.5. Mean: 20.0.
    """
    return pd.DataFrame({"dep_delay": [10, 30]})


# ================================================================
# TESTS
# ================================================================


@patch("app.simulation.engine.SimulationEngine._get_historical_data")
def test_run_hazard_simulation_direct_route(mock_get_db, mock_direct_flight_data):
    """Verifies that direct route simulations correctly compute basic delay probabilities
    and average delay metrics using vectorized pandas evaluation.
    """
    # Force our private database method to return our controlled fixture
    mock_get_db.return_value = mock_direct_flight_data

    # Execute the core simulation layer
    result = SimulationEngine.run_hazard_simulation(
        origin="LAX", destination="JFK", layovers=[]
    )

    # Assertions to validate contract architecture and math integrity
    assert result["status"] == "calculated"
    assert result["origin_airport"] == "LAX"
    assert result["destination_airport"] == "JFK"
    assert result["total_layovers"] == 0
    assert result["calculated_risk_factor"] == 0.5
    assert result["metrics"]["historical_sample_size"] == 4
    assert result["metrics"]["base_delay_probability"] == 0.5
    assert result["metrics"]["average_departure_delay_minutes"] == 15.0


@patch("app.simulation.engine.SimulationEngine._get_historical_data")
def test_run_hazard_simulation_multi_segment_route(
    mock_get_db, mock_segment_1_data, mock_segment_2_data
):
    """Ensures the routing algorithm correctly decomposes layovers into sequential
    legs and cascades the risk probabilities over multiple historical records.
    """
    # Configure the mock to return different dataframes sequentially for each loop iteration
    mock_get_db.side_effect = [mock_segment_1_data, mock_segment_2_data]

    layovers = [{"airport": "ORD"}]
    result = SimulationEngine.run_hazard_simulation(
        origin="LAX", destination="JFK", layovers=layovers
    )

    # Statistical combinations validation
    # Leg 1 Prob (0.5) + Leg 2 Prob (0.5) = Capped final risk 1.0
    # Global Mean Delay: (10.0 + 20.0) / 2 = 15.0
    assert result["status"] == "calculated"
    assert result["total_layovers"] == 1
    assert result["calculated_risk_factor"] == 1.0
    assert result["metrics"]["historical_sample_size"] == 4
    assert result["metrics"]["base_delay_probability"] == 0.5
    assert result["metrics"]["average_departure_delay_minutes"] == 15.0


@patch("app.simulation.engine.SimulationEngine._get_historical_data")
def test_run_hazard_simulation_empty_fallback(mock_get_db):
    """Validates the 'Fail-Fast' safeguard mechanism returns an intuitive informational
    payload if the database has zero records for the requested parameters.
    """
    # Force database layer to return an empty DataFrame
    mock_get_db.return_value = pd.DataFrame()

    result = SimulationEngine.run_hazard_simulation(
        origin="MAD", destination="BRL", layovers=[]
    )

    assert result["status"] == "insufficient_historical_data"
    assert result["calculated_risk_factor"] == 0.0
    assert "metrics" not in result
