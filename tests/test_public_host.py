"""The public-host header must only be honored for allowlisted hosts.

Behind the Cloudflare Worker, Railway rewrites ``X-Forwarded-Host`` to its own
hostname, so the Worker sends the browser-facing host in ``X-Northflow-Host``
instead. These tests pin down that Flask builds external URLs from that header
when it is allowlisted, and ignores it otherwise.
"""

from flask import request, url_for

from app import create_app
from app.middleware import (
    PUBLIC_HOST_HEADER,
    PublicHostMiddleware,
    parse_allowed_hosts,
)
from config import TestingConfig


def _app_with_public_hosts(monkeypatch, hosts):
    monkeypatch.setattr(TestingConfig, "PUBLIC_HOSTS", hosts, raising=False)
    application = create_app("testing")

    @application.route("/_where")
    def where():
        return f"{request.host}|{url_for('where', _external=True)}"

    return application.test_client()


def test_parse_allowed_hosts_normalizes():
    parsed = parse_allowed_hosts(" Northflow.Example , , other.example:8443 ")
    assert parsed == {"northflow.example", "other.example:8443"}
    assert parse_allowed_hosts("") == frozenset()
    assert parse_allowed_hosts(None) == frozenset()


def test_parse_allowed_hosts_tolerates_scheme_and_path():
    parsed = parse_allowed_hosts(
        "https://northflow.example/, http://other.example:8443/auth/callback"
    )
    assert parsed == {"northflow.example", "other.example:8443"}
    assert parse_allowed_hosts("https://") == frozenset()


def test_allowlisted_public_host_is_used_for_external_urls(monkeypatch):
    client = _app_with_public_hosts(monkeypatch, "northflow.example")

    response = client.get(
        "/_where",
        base_url="https://app-production.up.railway.app",
        headers={PUBLIC_HOST_HEADER: "northflow.example"},
    )

    host, external = response.get_data(as_text=True).split("|")
    assert host == "northflow.example"
    assert external == "https://northflow.example/_where"


def test_unlisted_public_host_is_ignored(monkeypatch):
    client = _app_with_public_hosts(monkeypatch, "northflow.example")

    response = client.get(
        "/_where",
        base_url="https://app-production.up.railway.app",
        headers={PUBLIC_HOST_HEADER: "evil.example"},
    )

    host, external = response.get_data(as_text=True).split("|")
    assert host == "app-production.up.railway.app"
    assert external == "https://app-production.up.railway.app/_where"


def test_header_ignored_when_no_public_hosts_configured(monkeypatch):
    client = _app_with_public_hosts(monkeypatch, "")

    response = client.get(
        "/_where",
        base_url="https://app-production.up.railway.app",
        headers={PUBLIC_HOST_HEADER: "northflow.example"},
    )

    host, _ = response.get_data(as_text=True).split("|")
    assert host == "app-production.up.railway.app"


def test_middleware_splits_port_into_server_name_and_port():
    captured = {}

    def wsgi_app(environ, start_response):
        captured.update(environ)
        start_response("200 OK", [])
        return [b""]

    middleware = PublicHostMiddleware(wsgi_app, ["northflow.example:8443"])
    environ = {
        "HTTP_HOST": "origin.internal",
        "SERVER_NAME": "origin.internal",
        "SERVER_PORT": "80",
        "HTTP_X_NORTHFLOW_HOST": "Northflow.Example:8443",
    }
    list(middleware(environ, lambda *a: None))

    assert captured["HTTP_HOST"] == "northflow.example:8443"
    assert captured["SERVER_NAME"] == "northflow.example"
    assert captured["SERVER_PORT"] == "8443"
