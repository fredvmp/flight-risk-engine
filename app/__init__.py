from flask import Flask
from app.database import db
from app.config import DevelopmentConfig



def create_app(config_class=DevelopmentConfig):
    """Application Factory to instantiate, configure, and assemble the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind the database instance to this app
    db.init_app(app)

    # Register Domain Blueprints
    from app.system.routes import system_bp
    from app.simulation.routes import simulation_bp

    app.register_blueprint(system_bp, url_prefix="/api/system")
    app.register_blueprint(simulation_bp, url_prefix="/api/simulation")

    return app