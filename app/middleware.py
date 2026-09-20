"""WSGI middleware for running behind the Cloudflare Worker on Railway.

The Worker in ``worker.js`` fetches the Railway origin URL, so the ``Host``
header Railway sees is the Railway hostname, not the public domain the browser
used. Railway's edge proxy also overwrites ``X-Forwarded-Host`` with that same
Railway hostname, so the standard ProxyFix approach cannot recover the public
host. Flask would then build every absolute URL (``url_for(_external=True)``,
including the OAuth redirect URIs) on the Railway hostname.

To work around that, the Worker sends the public host in a private header that
no intermediary rewrites. This middleware copies it into the WSGI environ, but
only when the value is on an explicit allowlist: the Railway hostname is
publicly reachable, and a spoofed host header must never be able to steer an
OAuth redirect to an attacker-chosen domain.
"""

PUBLIC_HOST_HEADER = "X-Northflow-Host"


def _normalize_host(entry):
    """Reduce one ``PUBLIC_HOSTS`` entry to a bare ``host[:port]``.

    Tolerates the ways a hostname tends to get pasted into a dashboard:
    surrounding whitespace, a ``https://`` scheme, a trailing slash or path,
    and mixed case.
    """
    entry = entry.strip()
    if "://" in entry:
        entry = entry.split("://", 1)[1]
    entry = entry.split("/", 1)[0]
    return entry.lower()


def parse_allowed_hosts(value):
    """Turn a comma-separated ``PUBLIC_HOSTS`` setting into a set of hosts."""
    if not value:
        return frozenset()
    hosts = (_normalize_host(entry) for entry in value.split(","))
    return frozenset(host for host in hosts if host)


class PublicHostMiddleware:
    """Rewrite the request host from a trusted, allowlisted proxy header."""

    def __init__(self, app, allowed_hosts, header=PUBLIC_HOST_HEADER):
        self.app = app
        self.allowed_hosts = frozenset(h.lower() for h in allowed_hosts)
        self.environ_key = "HTTP_" + header.upper().replace("-", "_")

    def __call__(self, environ, start_response):
        host = (environ.get(self.environ_key) or "").strip().lower()
        if host and host in self.allowed_hosts:
            environ["HTTP_HOST"] = environ["SERVER_NAME"] = host
            # "]" guards against a bare IPv6 literal being split on ":"
            if ":" in host and not host.endswith("]"):
                environ["SERVER_NAME"], environ["SERVER_PORT"] = host.rsplit(":", 1)
        return self.app(environ, start_response)
