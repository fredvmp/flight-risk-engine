import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()


class Config:
    """
    Base configuration.
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "flight-risk-secure-token-98765")

    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "flight_risk_db")

    # Construct the connection URI
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disable Flask-SQLAlchemy event tracking to save RAM
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuration settings specific to the local development environment."""
    DEBUG = True


class TestingConfig(Config):
    """
    Configuration settings tailored for running automated unit tests.
    """
    TESTING = True
    DEBUG = True
    # Isolates tests into a separate database to avoid mutating real data
    DB_NAME = os.getenv("DB_TEST_NAME", "flight_risk_test_db")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"
    )


class ProductionConfig(Config):
    """Configuration settings for secure production deployment."""
    DEBUG = False
    TESTING = False
