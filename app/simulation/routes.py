from flask import Blueprint, jsonify, request
from app.simulation.engine import SimulationEngine
from app.simulation.models import SimulationHistory
from app.database import db

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

    # Persist successful calculations into the database
    if result.get("status") == "calculated":
        try:
            # Instantiate the history model mapping metrics from the engine payload
            audit_entry = SimulationHistory(
                origin=origin.upper(),
                destination=destination.upper(),
                total_layovers=result.get("total_layovers", 0),
                calculated_risk_factor=result.get("calculated_risk_factor", 0.0)
            )
            
            # Push the entity to the unit of work and flush to PostgreSQL
            db.session.add(audit_entry)
            db.session.commit()
            
        except Exception as db_error:
            # Rollback database state to maintain persistence sanity if it fails
            db.session.rollback()
            # Log the error but allow the request to finish so the user gets their analytical response
            print(f"[PERSISTENCE ERROR]: Failed to log simulation history. Details: {str(db_error)}")

    return jsonify(result), 200






@simulation_bp.route('/history', methods=['GET'])
def get_simulation_history():
    """Audit endpoint that fetches the historical logs of all calculated flight risks."""
    try:
        # We retrieve the records sorted from the most recent
        records = SimulationHistory.query.order_by(SimulationHistory.created_at.desc()).all()

        # We convert SQLAlchemy objects to JSON dictionaries using your 'to_dict()' method
        history_payload = [record.to_dict() for record in records]

        return jsonify({
            "status": "success",
            "count": len(history_payload),
            "history": history_payload
        }), 200

    except Exception as e:
        # Fallback in case the table doesn't exist yet or the connection fails
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve simulation history. Details: {str(e)}"
        }), 500
