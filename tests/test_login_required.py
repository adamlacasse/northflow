"""Verify every protected route redirects an unauthenticated request to login.

No database is touched here: an unauthenticated request must be rejected by
the `login_required` decorator before any DAL/service call happens.
"""

import pytest

# (method, path) for every route decorated with @login_required in
# app/routes/main.py. /health and /auth/* are intentionally excluded, as
# they don't require authentication.
PROTECTED_ROUTES = [
    ("GET", "/"),
    ("GET", "/questions"),
    ("GET", "/summary"),
    ("GET", "/checkins"),
    ("GET", "/checkins/new"),
    ("POST", "/checkins/new"),
    ("GET", "/checkins/1"),
    ("POST", "/checkins/1/edit"),
    ("POST", "/checkins/1/delete"),
    ("POST", "/questions/new"),
    ("POST", "/questions/1/edit"),
    ("POST", "/questions/1/delete"),
    ("POST", "/checkins/1/answers/1"),
    ("POST", "/checkins/1/answers/1/delete"),
]


@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
def test_unauthenticated_request_redirects_to_login(client, method, path):
    response = client.open(path, method=method)

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")


@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
def test_unauthenticated_request_flashes_warning(client, method, path):
    response = client.open(path, method=method, follow_redirects=True)

    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data


def test_health_does_not_require_login(client):
    # /health should not redirect to login even though it may 503 without a
    # real database connection.
    response = client.get("/health")
    assert response.status_code != 302
