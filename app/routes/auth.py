"""Authentication routes for OAuth login/logout."""

import logging
from functools import wraps
from typing import Any, Dict

from authlib.integrations.base_client import OAuthError
from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.auth import oauth
from app.dal import DatabaseError
from app.dal.oauth_users import (
    create_oauth_user,
    get_user_by_email,
    get_user_by_oauth,
    update_last_login,
)
from config import Config

bp = Blueprint("auth", __name__, url_prefix="/auth")
logger = logging.getLogger(__name__)

AUTH_LOGIN = "auth.login"
AUTH_ERROR_MESSAGE = "Authentication failed. Please try again."


def _db_creds() -> Dict[str, Any]:
    """Get database credentials from environment config."""
    return {
        "host": Config.DB_HOST,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "database": Config.DATABASE,
        "port": Config.DB_PORT,
    }


def login_required(f):
    """Decorator to require user authentication for routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        logger.debug(f"login_required check for {f.__name__}: user_id={user_id}")
        if "user_id" not in session:
            logger.warning(f"Unauthorized access attempt to {f.__name__}")
            flash("Please log in to access this page.", "warning")
            return redirect(url_for(AUTH_LOGIN))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/login")
def login():
    """Show login page with OAuth provider buttons."""
    return render_template("login.html")


@bp.route("/login/google")
def login_google():
    """Redirect to Google OAuth authorization."""
    redirect_uri = url_for("auth.callback_google", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route("/login/github")
def login_github():
    """Redirect to GitHub OAuth authorization."""
    redirect_uri = url_for("auth.callback_github", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)


@bp.route("/callback/google")
def callback_google():
    """Handle Google OAuth callback and create/login user."""
    try:
        # Get OAuth token from Google
        token = oauth.google.authorize_access_token()
        logger.info("Google OAuth token received successfully")

        # Get user info from Google
        user_info = token.get("userinfo")
        if not user_info:
            user_info = oauth.google.get("userinfo").json()

        # Extract user data
        oauth_id = user_info.get("sub")  # Google's unique user ID
        email = user_info.get("email")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")

        logger.info(f"Processing Google OAuth for email: {email}, oauth_id: {oauth_id}")

        if not oauth_id or not email:
            logger.error("Google OAuth callback missing required fields")
            flash("Authentication failed: Missing user information", "danger")
            return redirect(url_for(AUTH_LOGIN))

        # Get database credentials from environment config
        db_creds = _db_creds()
        logger.info(
            f"Database credentials loaded: host={db_creds['host']}, "
            f"database={db_creds['database']}"
        )

        # Check if user already exists
        logger.info("Checking if user exists by OAuth ID...")
        user = get_user_by_oauth(db_creds, "google", oauth_id)
        logger.info(
            f"User lookup by OAuth ID result: {'found' if user else 'not found'}"
        )

        if not user:
            # Check if email is already in use by another provider
            logger.info("Checking if email is already registered...")
            existing_email = get_user_by_email(db_creds, email)
            if existing_email:
                logger.warning(f"Email {email} already in use with different provider")
                flash(
                    "This email is already registered with a different provider.",
                    "warning",
                )
                return redirect(url_for(AUTH_LOGIN))

            # Create new user
            logger.info(f"Creating new user: {email}")
            user_id = create_oauth_user(
                db_creds,
                oauth_provider="google",
                oauth_id=oauth_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            logger.info(f"Created new Google OAuth user: {email} (ID: {user_id})")
            flash(
                f"Welcome, {first_name}! Your account has been created.",
                "success",
            )
        else:
            user_id = user["id"]
            logger.info(f"Google OAuth login for user: {email} (ID: {user_id})")
            flash(
                f"Welcome back, {user.get('first_name', first_name)}!",
                "success",
            )

        # Update last login
        logger.info(f"Updating last login for user {user_id}")
        logger.info("Setting session variables...")
        session.permanent = True
        session["user_id"] = user_id
        session["oauth_provider"] = "google"
        session["oauth_id"] = oauth_id
        session["email"] = email
        session["user_name"] = f"{first_name} {last_name}".strip()

        logger.info(f"Google OAuth session created for user {user_id}: {email}")
        logger.info("Redirecting to questions page...")

        return redirect(url_for("main.questions"))

    except OAuthError as error:
        logger.error(f"Google OAuth error: {error}", exc_info=True)
        flash(AUTH_ERROR_MESSAGE, "danger")
        return redirect(url_for(AUTH_LOGIN))
    except DatabaseError as db_error:
        logger.error(f"Database error in Google callback: {db_error}", exc_info=True)
        flash("Database connection error. Please try again later.", "danger")
        return redirect(url_for(AUTH_LOGIN))
    except Exception as exc:
        logger.error(f"Unexpected error in Google callback: {exc}", exc_info=True)
        logger.error(f"Error type: {type(exc).__name__}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        flash(AUTH_ERROR_MESSAGE, "danger")
        return redirect(url_for(AUTH_LOGIN))


@bp.route("/callback/github")
def callback_github():
    """Handle GitHub OAuth callback and create/login user."""
    try:
        # Get OAuth token from GitHub
        token = oauth.github.authorize_access_token()

        # Get user info from GitHub
        resp = oauth.github.get("user", token=token)
        user_info = resp.json()

        # Extract user data
        oauth_id = str(user_info.get("id"))  # GitHub's unique user ID
        email = user_info.get("email")
        name = user_info.get("name", "")
        login = user_info.get("login", "")  # GitHub username

        # If email is private, fetch from emails endpoint
        if not email:
            emails_resp = oauth.github.get("user/emails", token=token)
            emails = emails_resp.json()
            # Find primary verified email
            for email_obj in emails:
                if email_obj.get("primary") and email_obj.get("verified"):
                    email = email_obj.get("email")
                    break

        if not oauth_id or not email:
            logger.error("GitHub OAuth callback missing required fields")
            flash("Authentication failed: Missing user information", "danger")
            return redirect(url_for(AUTH_LOGIN))

        # Parse name or use username as fallback
        name_parts = name.split(" ", 1) if name else [login, ""]
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Get database credentials from environment config
        db_creds = _db_creds()

        # Check if user already exists
        user = get_user_by_oauth(db_creds, "github", oauth_id)

        if not user:
            # Check if email is already in use by another provider
            existing_email = get_user_by_email(db_creds, email)
            if existing_email:
                logger.warning(f"Email {email} already in use with different provider")
                flash(
                    "This email is already registered with a different provider.",
                    "warning",
                )
                return redirect(url_for(AUTH_LOGIN))

            # Create new user
            user_id = create_oauth_user(
                db_creds,
                oauth_provider="github",
                oauth_id=oauth_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            logger.info(f"Created new GitHub OAuth user: {email} (ID: {user_id})")
            flash(f"Welcome, {first_name}! Your account has been created.", "success")
        else:
            user_id = user["id"]
            logger.info(f"GitHub OAuth login for user: {email} (ID: {user_id})")
            flash(f"Welcome back, {user.get('first_name', first_name)}!", "success")

        # Update last login
        update_last_login(db_creds, user_id)

        # Store user session info
        session.permanent = True
        session["user_id"] = user_id
        session["oauth_provider"] = "github"
        session["oauth_id"] = oauth_id
        session["email"] = email
        session["user_name"] = name or login

        logger.info(f"GitHub OAuth session created for user {user_id}: {email}")

        return redirect(url_for("main.questions"))

    except OAuthError as error:
        logger.error(f"GitHub OAuth error: {error}", exc_info=True)
        flash(AUTH_ERROR_MESSAGE, "danger")
        return redirect(url_for(AUTH_LOGIN))
    except Exception as exc:
        logger.error(f"Unexpected error in GitHub callback: {exc}", exc_info=True)
        flash("An error occurred during login. Please try again.", "danger")
        return redirect(url_for(AUTH_LOGIN))


@bp.route("/logout")
def logout():
    """Clear session and log out user."""
    user_name = session.get("user_name", "User")

    # Clear all session data
    session.clear()

    logger.info(f"User logged out: {user_name}")
    flash("You have been logged out successfully.", "info")

    return redirect(url_for(AUTH_LOGIN))
