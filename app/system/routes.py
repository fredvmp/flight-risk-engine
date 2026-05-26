from flask import Blueprint, jsonify
from sqlalchemy import text
from app.database import db


system_bp = Blueprint('system', __name__)


@system_bp.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint to verify infrastructure status."""

    try:
        db.session.execute(text("SELECT 1"))

        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'service': 'flight-risk-engine'
        }), 200

    except Exception as e:
        print(f"[HEALTH CHECK ERROR]: {str(e)}")

        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'message': 'Database connection failed'
        }), 500
