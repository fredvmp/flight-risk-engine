import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig
from app.database import db

# Determine the execution environment from OS variables
ENV = os.getenv("FLASK_ENV", "development")

# Assign the appropriate configuration class based on the environment
if ENV == "production":
    current_config = ProductionConfig
else:
    current_config = DevelopmentConfig

# Invoke the Application Factory to build the instance
app = create_app(config_class=current_config)

with app.app_context():
    db.create_all()
print("[DATABASE]: Tables synchronized successfully.")

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=app.config["DEBUG"],
    )
