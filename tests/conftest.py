"""Shared pytest fixtures for the non-integration test suite.

These fixtures build a Flask app using TestingConfig (CSRF disabled, no
external OAuth calls made at import time) so the whole suite can run with
`pytest -m "not integration"` and no database available. Tests that need a
real MySQL connection must be marked with `@pytest.mark.integration`.
"""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest

from app import create_app


@pytest.fixture()
def app():
    """A Flask app instance configured for testing."""
    application = create_app("testing")
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    yield application


@pytest.fixture()
def client(app):
    """A Flask test client with no user logged in."""
    return app.test_client()


def login_as(client, user_id: int, name: str = "Test User"):
    """Log a given user id into the test client's session."""
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["email"] = f"user{user_id}@example.com"
        sess["oauth_provider"] = "google"
        sess["oauth_id"] = f"oauth-{user_id}"


@pytest.fixture()
def logged_in_client(client):
    """A test client logged in as user id 1."""
    login_as(client, 1)
    return client
