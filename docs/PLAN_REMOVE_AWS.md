# Plan: Remove All AWS / CDK References from NorthFlow

> **Status:** Ready for execution
> **Created:** 2026-04-03
> **Purpose:** Completely remove all AWS infrastructure code, CDK tooling, AWS-specific
> deployment scripts, and any textual references to AWS services from the repository.
> The owner has already deleted all AWS artifacts from the AWS Console.

---

## Scope

This plan covers:

1. Deleting the entire `infra/` directory (CDK project)
2. Updating documentation to remove AWS references
3. Cleaning up `.gitignore` and `.dockerignore`
4. Removing AWS-specific VS Code settings
5. Removing the `infra/text` sync TODO item
6. Updating the `docs/DECISIONS.md` and `docs/DEPLOYMENT_ACTIVE.md` files
7. No test changes are required (tests have no AWS dependencies)

---

## Pre-Execution Checklist

Before starting, verify:

- [ ] You are on a feature branch (not `main`)
- [ ] The repository lints cleanly before changes: `invoke lint`

---

## Step-by-Step Tasks

### Task 1: Delete the entire `infra/` directory

**What:** The `infra/` directory is a complete AWS CDK project (TypeScript). Every file
in it is AWS-specific and must be deleted.

**Action:** Delete the entire directory tree.

**Files to delete (all of them):**

- `infra/package.json`
- `infra/package-lock.json`
- `infra/tsconfig.json`
- `infra/cdk.json`
- `infra/bin/northflow.ts`
- `infra/ssm-bootstrap.json`
- `infra/ssm-bootstrap-from-s3.json`
- `infra/ssm-run-app.json`
- `infra/ssm-restart-with-oauth.json`
- `infra/restart-with-oauth.sh`

**Command:**

```bash
rm -rf infra/
```

**Verification:** `ls infra/` should return "No such file or directory".

---

### Task 2: Update `.gitignore` — remove CDK and AWS sections

**What:** The `.gitignore` file has two AWS-related sections that must be removed.

**File:** `.gitignore`

**Remove lines 209–220** (the entire block below):

```gitignore
# CDK / TypeScript / Node.js
infra/node_modules/
infra/cdk.out/
infra/dist/
infra/*.js
infra/*.d.ts
infra/.cdk.staging/
infra/cdk.context.json
infra/text/

# AWS / Deployment
.aws/
```

**Keep** the `*.pem` and `*.key` lines that follow — those are generic security
entries not specific to AWS.

**Verification:** `grep -i 'cdk\|infra\|\.aws' .gitignore` should return no results.

---

### Task 3: Update `.dockerignore` — remove CDK/infra entries

**What:** Three lines reference `infra/` or `cdk.out/` and should be removed.

**File:** `.dockerignore`

**Remove these three lines:**

```
infra/node_modules/
infra/cdk.out/
cdk.out/
```

**Verification:** `grep -i 'cdk\|infra' .dockerignore` should return no results.

---

### Task 4: Update `.vscode/settings.json` — remove `amazonlinux` from spell checker

**What:** The `cSpell.words` array includes `"amazonlinux"`, which is AWS-specific.

**File:** `.vscode/settings.json`

**Action:** Remove the line `"amazonlinux",` from the `cSpell.words` array.

**Before:**

```json
"cSpell.words": [
    "amazonlinux",
    "Authlib",
```

**After:**

```json
"cSpell.words": [
    "Authlib",
```

**Verification:** `grep -i amazon .vscode/settings.json` should return no results.

---

### Task 5: Rewrite `docs/DEPLOYMENT_ACTIVE.md`

**What:** This file is heavily AWS-specific (EC2, RDS, SSM, Secrets Manager, ACM, ALB,
Elastic Beanstalk, Cloudflare ACM validation). It must be rewritten to reflect that
the application no longer has a cloud deployment target.

**File:** `docs/DEPLOYMENT_ACTIVE.md`

**Action:** Replace the entire file contents with the following:

```markdown
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
```

**Verification:** `grep -i 'aws\|ec2\|rds\|ssm\|acm\|cloudfront\|ALB\|Beanstalk\|CDK\|Fargate\|ECS\|EKS' docs/DEPLOYMENT_ACTIVE.md` should return no results.

---

### Task 6: Rewrite `docs/DECISIONS.md`

**What:** This file references EC2 and RDS. It must be updated to reflect that
there is no cloud deployment.

**File:** `docs/DECISIONS.md`

**Action:** Replace the entire file contents with:

```markdown
# Decision Log

> **Note:** For open questions on architecture and data model, see [../TODO.md](../TODO.md).

## Deployment Runtime (Active)

- Application runtime: Docker container (local / Docker Compose)
- Database: MySQL 8.0 (local or containerized)
- Cloud deployment: explicitly removed; no active cloud target
```

**Verification:** `grep -i 'aws\|ec2\|rds\|ecs\|fargate' docs/DECISIONS.md` should return no results.

---

### Task 7: Update `README.md` — remove the "Deployment (AWS CDK)" section

**What:** Lines 228–238 contain an AWS CDK deployment section that must be removed.

**File:** `README.md`

**Action:** Delete lines 228–238 (the entire block from `## Deployment (AWS CDK)` through the AWS CLI prerequisite). Replace with a brief Docker Compose deployment note.

**Remove this block (lines 228–238):**

```markdown
## Deployment (AWS CDK)

NorthFlow deployment is **AWS-only** via CDK. See
[docs/DEPLOYMENT_ACTIVE.md](docs/DEPLOYMENT_ACTIVE.md) for the target architecture and
migration contract. CDK provisioning is currently a work in progress.

### Prerequisites

- AWS CLI configured (`aws sts get-caller-identity` works)
- Node 18+ / npm
- Docker
```

**Replace with:**

```markdown
## Deployment

NorthFlow can be run locally or via Docker Compose. See
[docs/DEPLOYMENT_ACTIVE.md](docs/DEPLOYMENT_ACTIVE.md) for the deployment model and
migration contract.

### Prerequisites

- Docker (for containerized runs)
```

**Verification:** `grep -i 'aws\|cdk' README.md` should return no results.

---

### Task 8: Update `TODO.md` — remove the `infra/text` sync item

**What:** The last TODO item references syncing files into `infra/text/`, which no
longer exists.

**File:** `TODO.md`

**Action:** Delete the last line (line 16):

```markdown
- [ ] After any README/TODO changes, sync `infra/text/asset.9ace2a67483fdbe49d08c0de2e18c743664aceb8bca1aa29fc42590b955a30da/README.md` and `infra/text/asset.9ace2a67483fdbe49d08c0de2e18c743664aceb8bca1aa29fc42590b955a30da/TODO.md` to match.
```

**Verification:** `grep -i 'infra' TODO.md` should return no results.

---

### Task 9: Verify no remaining AWS references exist

**Action:** Run a comprehensive search across the entire repository to confirm no AWS
references remain.

**Command:**

```bash
grep -ri --include='*.py' --include='*.ts' --include='*.js' --include='*.json' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.sh' \
  --include='*.html' --include='*.css' --include='*.toml' --include='*.cfg' \
  --include='*.ini' --include='*.txt' \
  -E '\baws\b|\bcdk\b|\bamazon\b|\bec2\b|\brds\b|\bssm\b|\bacm\b|\biam\b|\bs3\b|\becs\b|\becr\b|\bfargate\b|\bcloudformation\b|\bcloudfront\b|\belastic.?beanstalk\b|\bsecretsmanager\b' \
  --exclude-dir=.git .
```

**Expected:** Zero results. If any hits appear, evaluate whether they are:

- False positives (e.g., "class" matching "s3" is not a hit)
- Genuine AWS references that need removal

**Acceptable false positives:**

- The word "passwords" matching `ss` (not a real match with `\b` boundaries)
- CSS class names or HTML content that happen to contain substrings

---

### Task 10: Run linters to verify nothing is broken

**Commands:**

```bash
invoke lint-python
invoke lint-markdown
```

Note: `invoke lint-sql` and `invoke lint-html` are unaffected by these changes but
can be run for completeness.

**Expected:** All linters pass cleanly.

---

## Tests

### Are any test changes required?

**No.** After reviewing both test files:

- **`tests/test_connection.py`:** Tests the `DatabaseConnection` DAL class against a
  local MySQL database. Contains zero AWS references. No changes needed.

- **`tests/test_sql_injection.py`:** Tests SQL injection prevention via stored
  procedures and parameterized queries. Contains zero AWS references. No changes needed.

Neither test file imports, references, or depends on any AWS SDK, CDK construct,
or AWS service. The test suite is entirely local/database-focused.

---

## Files Changed Summary

| Action | File/Directory | Reason |
|--------|---------------|--------|
| **DELETE** | `infra/` (entire directory, 10 files) | AWS CDK project — all AWS-specific |
| **EDIT** | `.gitignore` | Remove CDK/infra/AWS ignore entries (lines 209–220) |
| **EDIT** | `.dockerignore` | Remove infra/cdk.out entries (3 lines) |
| **EDIT** | `.vscode/settings.json` | Remove `"amazonlinux"` from spell checker |
| **REWRITE** | `docs/DEPLOYMENT_ACTIVE.md` | Remove all AWS architecture references |
| **REWRITE** | `docs/DECISIONS.md` | Remove EC2/RDS references |
| **EDIT** | `README.md` | Replace AWS CDK deployment section |
| **EDIT** | `TODO.md` | Remove `infra/text` sync item |

## Files NOT Changed (Confirmed Clean)

| File | Reason no change needed |
|------|------------------------|
| `config.py` | No AWS references; uses generic env vars |
| `app/auth.py` | OAuth only; no AWS |
| `docker-compose.yml` | Local Docker only; no AWS |
| `Dockerfile` (root) | Generic Python image; no AWS |
| `deploy/Dockerfile` | Generic Python image; no AWS |
| `deploy/entrypoint.sh` | Generic shell script; no AWS |
| `deploy/migrate.sh` | Generic migration script; no AWS |
| `pyproject.toml` | No AWS dependencies |
| `requirements.txt` | No AWS dependencies |
| `tasks.py` | No AWS references |
| `.env.example` | Generic env vars; no AWS |
| `.sqlfluff` | SQL linter config; no AWS |
| `run.py` | App entry point; no AWS |
| `pytest.ini` | Test config; no AWS |
| `tests/test_connection.py` | No AWS references |
| `tests/test_sql_injection.py` | No AWS references |
| All `app/` source files | No AWS imports or references |
| All `app/templates/` files | No AWS references |
| All `app/static/` files | No AWS references |
