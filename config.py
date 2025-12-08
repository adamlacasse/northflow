"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


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


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
