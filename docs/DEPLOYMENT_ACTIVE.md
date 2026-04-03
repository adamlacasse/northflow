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

NorthFlow runs locally or via Docker Compose. There is no cloud deployment target
at this time.

- **Application runtime:** Docker container (Flask + gunicorn) or direct `python run.py`
- **Process model:** Docker Compose (`docker-compose.yml`) for production-like local runs
- **Database:** MySQL 8.0 (local install or Docker Compose `db` service)
- **Secrets:** Environment variables loaded from `.env`

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

Command:

```bash
MIGRATE_MODE=schema ./deploy/migrate.sh
```

⚠️ Never run this against an existing environment.

### 3.2 Apply Objects (Safe — Run on Every Deploy)

**Purpose**: Ensure required database objects exist.

Characteristics:
Applies views, stored procedures, and functions
Uses DROP … IF EXISTS + CREATE …
Safe and repeatable
Deterministic

Command:

```bash
MIGRATE_MODE=objects ./deploy/migrate.sh
```

This step must complete successfully before the web application starts.

## 4. Application Startup Contract

The correct startup order is:

1. Database is reachable
2. apply_schema_objects has run successfully
3. Web container starts

The application must not serve traffic unless required DB routines exist.

## 5. Health Check Semantics

The /health endpoint enforces readiness:

- 503 — database unreachable
- 503 — database reachable but required routines missing
- 200 — database reachable and schema objects present

This prevents race conditions where routes attempt to call missing procedures.

## 6. Operational Notes

- Schema bootstrap is manual and intentional
- Schema object application is automatic and repeatable
- Deployment scripts default to safe behavior
- Logs are obtained from container stdout/stderr

## 7. Rule for AI Agents

Agents must:

- Respect the database migration contract
- Run apply_schema_objects before starting the app
- Avoid introducing cloud services without an explicit decision update

If uncertain, **stop and ask** rather than inventing infrastructure.
