"""Flask application factory."""

from flask import Flask


def create_app(config_name="default"):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name (development, production, testing, default)

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    from config import config

    app.config.from_object(config[config_name])

    # Register blueprints
    from app.routes import main

    app.register_blueprint(main.bp)

    return app
