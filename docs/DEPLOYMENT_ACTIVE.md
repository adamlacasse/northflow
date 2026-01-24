# NorthFlow — Active Deployment Model

> **Status:** Active  
> **Audience:** Humans and AI agents working in this repo  
> **Scope:** Current reality + supported future options only  
> **Related:** See [../TODO.md](../TODO.md) for open questions on app logic and data model.

---

## 1. Source of Truth

This document is the **authoritative description** of how NorthFlow is deployed
today.

If any other file, diagram, or comment conflicts with this document:
**this document wins.**

---

## 2. Current Reality (Authoritative)

NorthFlow is deployed using the following architecture:

- **Application runtime:** Single EC2 instance
- **Process model:** Docker container (Flask + gunicorn)
- **Database:** Amazon RDS MySQL
- **Networking:** EC2 connects to RDS via private networking
- **Secrets:** Environment variables (SSM / Secrets Manager optional)
- **Public access:** EC2 public DNS (ALB / HTTPS may be added later)

This is the **only active deployment model**.

> **CDK Status:** Infrastructure-as-Code is in progress. The above architecture is the
> **target state**. Provisioning and deployment automation via CDK (`infra/`) are
> still being finalized.

---

## 3. Explicit Non-Goals (Right Now)

The following are **not** part of the current architecture:

- ECS / Fargate
- EKS / Kubernetes
- App Runner
- Blue/green or canary deployments
- Autoscaling
- Multi-AZ or multi-region setups

These may be revisited later, but **must not be introduced without an explicit
decision update**.

---

## 4. Database Migration Contract (Critical)

NorthFlow intentionally separates **destructive bootstrap** from **repeatable
schema application**.

### 4.1 Bootstrap (Destructive — One Time Only)

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

### 4.2 Apply Objects (Safe — Run on Every Deploy)

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

## 5. Application Startup Contract

The correct startup order is:

1. Database is reachable
2. apply_schema_objects has run successfully
3. Web container starts

The application must not serve traffic unless required DB routines exist.

## 6. Health Check Semantics

The /health endpoint enforces readiness:

- 503 — database unreachable
- 503 — database reachable but required routines missing
- 200 — database reachable and schema objects present

This prevents race conditions where routes attempt to call missing procedures.

## 7. Operational Notes

- Schema bootstrap is manual and intentional
- Schema object application is automatic and repeatable
- Deployment scripts default to safe behavior
- Logs are obtained from container stdout/stderr
- Debugging is done directly on the EC2 instance

## 8. Future-Safe Evolution (Allowed With Decision Update)

The following upgrades are allowed only via an explicit decision update:

- Add ALB + HTTPS (ACM)
- Migrate runtime to Elastic Beanstalk
- Introduce ECS/Fargate
- Add CI/CD automation
- Add monitoring and alerts

Until documented otherwise, EC2 + Docker + RDS is the source of truth.

## 9. Rule for AI Agents

Agents must:

- Respect the database migration contract
- Run apply_schema_objects before starting the app
- Avoid introducing new AWS services implicitly
- Avoid resurrecting ECS/Fargate or other deprecated models

If uncertain, **stop and ask** rather than inventing infrastructure.
