from flask import Blueprint, jsonify, request
from app.simulation.engine import SimulationEngine


simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/run', methods=['POST'])
def run_simulation():
    """Endpoint to trigger the flight risk simulation engine based on flight parameters."""

    # Analyze and validate the incoming JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    # Extract fields
    origin = data.get('origin')
    destination = data.get('destination')
    layovers = data.get('layovers')

    # Fail-Fast
    if not origin or not isinstance(origin, str) or len(origin) != 3:
        return jsonify({"error": "Missing or invalid 'origin'. Must be a 3-letter code."}), 400

    if not destination or not isinstance(destination, str) or len(destination) != 3:
        return jsonify({"error": "Missing or invalid 'destination'. Must be a 3-letter code."}), 400

    if layovers is None or not isinstance(layovers, list):
        return jsonify({"error": "Missing or invalid 'layovers'. Must be a list of connections."}), 400

    result = SimulationEngine.run_hazard_simulation(origin, destination, layovers)
    return jsonify(result), 200
