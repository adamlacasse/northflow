"""Flask application factory."""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from app.auth import init_oauth

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)


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

    # Initialize CSRF protection
    csrf.init_app(app)

    # Initialize rate limiting
    limiter.init_app(app)

    # Initialize OAuth authentication
    init_oauth(app)

    # Add security headers
    @app.after_request
    def set_security_headers(response):
        """Set HTTP security headers."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'"
        )
        return response

    # Register blueprints
    from app.routes import auth, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    return app
