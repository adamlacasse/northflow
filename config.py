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
    DB_PORT = int(os.getenv("DB_PORT", "3306"))

    # Flask
    # SECRET_KEY MUST be set in environment for production
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable is required. "
            "Generate with: python3 -c 'import secrets; "
            "print(secrets.token_hex(32))'"
        )
    DEBUG = False
    TESTING = False

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit on CSRF tokens

    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200/hour"  # Global default


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    # For local development without HTTPS
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    # For testing without HTTPS
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
