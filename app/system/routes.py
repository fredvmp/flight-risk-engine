from flask import Blueprint, jsonify


system_bp = Blueprint('system', __name__)


@system_bp.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint to verify infrastructure status."""
    return jsonify({
        'status': 'healthy',
        'service': 'flight-risk-engine'
    }), 200



