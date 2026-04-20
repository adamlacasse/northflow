"""OAuth authentication integration for NorthFlow.

This module provides OAuth 2.0 authentication with Google.
No passwords are stored in the database - only OAuth provider IDs.
"""

from authlib.integrations.flask_client import OAuth

# OAuth instance - will be initialized in app factory
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with Google provider.

    Args:
        app: Flask application instance
    """
    oauth.init_app(app)

    # Register Google OAuth provider
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
        client_kwargs={"scope": "openid email profile"},
    )

    return oauth
