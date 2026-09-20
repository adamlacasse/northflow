# NorthFlow — Deployment Model

> **Status:** Active
> **Audience:** Humans and AI agents working in this repo
> **Scope:** Current reality only

---

## 1. Source of Truth

This document is the **authoritative description** of how NorthFlow is deployed
today.

If any other file, diagram, or comment conflicts with this document:
**this document wins.**

---

## 2. Current Reality (Authoritative)

NorthFlow is deployed on Railway (or run locally via Docker Compose).

- **Application runtime:** Docker container (Flask + gunicorn) on Railway
- **Database:** MySQL 8.0 on Railway (managed service)
- **Networking:** Web service connects to MySQL over Railway's private network
- **Secrets:** Environment variables configured in the Railway dashboard
- **TLS:** Handled automatically by Railway
- **DNS:** Cloudflare CNAME pointing to Railway's domain
- **Local development:** Docker Compose (`docker-compose.yml`) or direct `python run.py`

> **Gap (unverified):** the repository also contains a Cloudflare Worker
> (`worker.js`, `wrangler.toml`) configured to front `northflow.adamlacasse.dev/*`
> with a cold-start loading shell. Whether it is deployed, and whether the
> hostname is proxied (which a Worker route requires) or DNS-only (which the DNS
> bullet above and `PLAN_DEPLOY_RAILWAY.md` both state), has not been confirmed.
> Until it is, treat this section as describing the Railway side only. See
> [../TODO.md](../TODO.md) item **P3-2**.

### 2.1 Public hostname behind the Worker (Required)

The Worker fetches the Railway origin URL, so Railway sees its own hostname in
`Host`, and Railway's edge proxy **overwrites `X-Forwarded-Host`** with that
same hostname (confirmed 2026-09-20: a request to the Railway domain with a
spoofed `X-Forwarded-Host` still produced a Railway-domain OAuth
`redirect_uri`). Flask therefore cannot learn the public domain from the
standard headers, and without help it builds OAuth callbacks on
`*.up.railway.app`, which Google rejects with `redirect_uri_mismatch`.

The fix has two halves that must both be deployed:

- `worker.js` sends the browser-facing host in the private header
  `X-Northflow-Host`.
- Flask (`app/middleware.py`) copies that header into the request host, but
  **only** if the value appears in the `PUBLIC_HOSTS` environment variable
  (comma-separated). Set `PUBLIC_HOSTS=northflow.adamlacasse.dev` on the
  Railway web service. An empty value disables the header entirely.

The allowlist is a security control, not a convenience: the Railway hostname is
publicly reachable, and an unvalidated host header would let anyone steer the
OAuth redirect to a domain they control.

---

## 3. Database Migration Contract (Critical)

NorthFlow intentionally separates **destructive bootstrap** from **repeatable
schema application**.

### 3.1 Bootstrap (Destructive — One Time Only)

**Purpose:** Initialize a brand-new, empty database.

Characteristics:

- May include `DROP DATABASE`
- Creates tables, views, procedures, functions
- May seed data
- **Never repeatable**

Command (local):

```bash
MIGRATE_MODE=schema ./deploy/migrate.sh
```

Command (Railway CLI):

```bash
MIGRATE_MODE=schema railway run --service web -- /app/deploy/migrate.sh
```

⚠️ Never run this against an existing environment.

### 3.2 Apply Objects (Safe — Run on Every Deploy)

**Purpose**: Ensure required database objects exist.

Characteristics:
Applies views, stored procedures, and functions
Uses DROP … IF EXISTS + CREATE …
Safe and repeatable
Deterministic

This runs automatically on every deploy via `deploy/entrypoint.sh` before
gunicorn starts. It can also be run manually:

```bash
MIGRATE_MODE=objects ./deploy/migrate.sh
```

## 4. Application Startup Contract

The correct startup order is:

1. Database is reachable
2. apply_schema_objects has run successfully (automatic via entrypoint)
3. Web container starts

The application must not serve traffic unless required DB routines exist.

## 5. Health Check Semantics

The /health endpoint enforces readiness:

- 503 — database unreachable
- 503 — database reachable but required routines missing
- 200 — database reachable and schema objects present

Railway uses this endpoint to determine when to route traffic to the service.

## 6. Operational Notes

- Schema bootstrap is manual and intentional
- Schema object application is automatic on every deploy
- Deployment scripts default to safe behavior
- Logs are available in the Railway dashboard
- Deploys are triggered by pushing to the GitHub repo

## 7. Rule for AI Agents

Agents must:

- Respect the database migration contract
- Never run destructive bootstrap against an existing environment
- Avoid introducing new cloud services without an explicit decision update

If uncertain, **stop and ask** rather than inventing infrastructure.
