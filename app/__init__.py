"""Flask application factory."""

import os

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from app.auth import init_oauth
from app.middleware import PublicHostMiddleware, parse_allowed_hosts

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name=None):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name (development, production, testing, default)

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    from config import config

    selected_config = config_name or os.getenv("FLASK_ENV", "production")
    app.config.from_object(config.get(selected_config, config["default"]))

    # Behind the Cloudflare Worker, Railway rewrites X-Forwarded-Host to its
    # own hostname, so the public host arrives in a private header instead.
    # Honor it only for allowlisted hosts (PUBLIC_HOSTS). This wraps the app
    # first so it runs after ProxyFix and has the final say on the host.
    app.wsgi_app = PublicHostMiddleware(
        app.wsgi_app, parse_allowed_hosts(app.config.get("PUBLIC_HOSTS"))
    )
    # Trust the first reverse proxy for the scheme so generated URLs are
    # https behind Railway. x_host is deliberately off: Railway overwrites
    # that header with the wrong value (see app/middleware.py).
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

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
