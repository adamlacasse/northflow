import os
from dotenv import load_dotenv


load_dotenv()


"""
Multiple environments will be a future enhancement.
For CSC-6302, a single configuration environment is used.
"""


class Config:
    """Base configuration."""

    # Database
    DATABASE = "northflow"
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
