from flask import Blueprint, jsonify

simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/run', methods=['GET'])
def run_simulation():
    """Temporary endpoint to verify if the simulation blueprint is reachable."""
    return jsonify({
        'status': 'operational',
        'message': 'FlightRisk Engine simulation module loaded successfully.'
    }), 200
