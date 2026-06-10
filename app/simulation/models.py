from app.database import db
from datetime import datetime


class SimulationHistory(db.Model):
    """SQLAlchemy model representing the audit trail for calculated hazard simulations."""

    __tablename__ = "simulation_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin = db.Column(db.String(3), nullable=False)
    destination = db.Column(db.String(3), nullable=False)
    total_layovers = db.Column(db.Integer, nullable=False)
    calculated_risk_factor = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Serializes the SQLAlchemy database record into a clean Python dictionary."""
        return {
            "id": self.id,
            "origin_airport": self.origin,
            "destination_airport": self.destination,
            "total_layovers": self.total_layovers,
            "calculated_risk_factor": round(self.calculated_risk_factor, 4),
            "executed_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }