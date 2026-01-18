"""OAuth authentication integration for NorthFlow.

This module provides OAuth 2.0 authentication with Google and GitHub.
No passwords are stored in the database - only OAuth provider IDs.
"""

from authlib.integrations.flask_client import OAuth

# OAuth instance - will be initialized in app factory
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with Google and GitHub providers.

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

    # Register GitHub OAuth provider
    oauth.register(
        name="github",
        client_id=app.config["GITHUB_CLIENT_ID"],
        client_secret=app.config["GITHUB_CLIENT_SECRET"],
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

    return oauth
