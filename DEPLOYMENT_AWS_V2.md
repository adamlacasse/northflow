# NorthFlow on AWS (CDK TypeScript) — Architecture & Implementation Guide (Agent-Oriented)

Audience: AI coding agents working in this repo.
Goal: Stand up a production-grade, portfolio-friendly AWS deployment for an existing Python/Flask app using AWS CDK in **TypeScript**.

---

## 1) Goals

### Functional
- Deploy the existing **Flask monolith** (templates/static/routes/DAL) as a container.
- Provision **MySQL** on AWS and apply `app/database/schema.sql` (stored procedures/views included).
- Serve the app over HTTPS behind a load balancer with a stable domain.
- Use **Infrastructure as Code** (CDK) for all infra.

### Operational
- Repeatable deployment: `cdk deploy` builds/uses an image, deploys infra, runs schema task.
- Secrets are managed in **AWS Secrets Manager**, non-secrets in **SSM Parameter Store**.
- Logging to **CloudWatch Logs**.
- Minimal but correct networking/security posture.

### Portfolio signal
- ECS/Fargate + ALB + RDS + Secrets Manager + Route53/ACM
- One-off migration task
- Clear README + architecture doc (this document)

---

## 2) Non-goals (for v1)

- Multi-region, multi-account landing zones
- Kubernetes/EKS
- Full GitOps system or complex blue/green
- Complex service mesh
- Autoscaling/alarms beyond basics (can be added later)

---

## 3) Target Architecture (High Level)

**Client (Browser)**
  -> **Route53** (DNS)
  -> **ALB (HTTPS)** (ACM certificate)
  -> **ECS Fargate Service** (gunicorn + Flask)
  -> **RDS MySQL** (private subnet)

Support services:
- **Secrets Manager**: DB creds + Flask secret key + OAuth secret(s)
- **SSM Parameter Store**: non-secret config
- **CloudWatch Logs**: app logs + migration task logs
- **ECR**: container image repository

---

## 4) Repository Layout

Add two top-level directories, keep app structure intact:

northflow/
    app/...
    config.py
    run.py
    tasks.py
    tests/...

deploy/
    Dockerfile
    entrypoint.sh # web mode
    migrate.sh # migration mode (schema setup)

infra/ # CDK TypeScript project
    package.json
    cdk.json
    tsconfig.json
    bin/
        northflow.ts # CDK app entry
    lib/
        config.ts # env/config helpers
        network-stack.ts
        database-stack.ts
        app-stack.ts
        outputs.ts


---

## 5) Application Runtime Model

### 5.1 Container entrypoints (two “modes”)
The same container image must support:
1) **Web mode**: run gunicorn and serve Flask app
2) **Migration mode**: apply schema to RDS (run setup script)

This enables repeatable infra deploys without baking DB state into app startup.

### 5.2 Gunicorn requirement
In production we must not run Flask dev server.
- Use gunicorn (sync workers fine for v1).
- Health route: `/health` should be fast and not block on slow operations.

### 5.3 Config surface (env vars)
Standardize config via env vars (read by `config.py`):

Required:
- `FLASK_ENV` (e.g., `production`)
- `FLASK_SECRET_KEY` (secret)
- `DB_HOST` / `DB_PORT` / `DB_NAME`
- `DB_USER` / `DB_PASSWORD` (secret)
- OAuth:
  - `OAUTH_CLIENT_ID` (SSM or secret)
  - `OAUTH_CLIENT_SECRET` (secret)
  - `OAUTH_REDIRECT_URI` (SSM)

Optional:
- `RATE_LIMIT_*`
- `CSRF_*` (if needed)
- Anything else currently in `.env` becomes SSM/Secrets in AWS

---

## 6) Infrastructure Stacks (CDK)

All stacks should be explicit and composable. Prefer 3 stacks.

### 6.1 NetworkStack
Creates:
- VPC (2 AZ)
- Public subnets (ALB)
- Private subnets (ECS tasks + RDS)
- NAT Gateway (simplest)

Exports/outputs:
- VPC reference
- Subnet selections

Security posture:
- Nothing public except the ALB.

### 6.2 DatabaseStack
Creates:
- RDS MySQL instance (private subnet)
- DB security group (ingress only from ECS SG, defined later)
- Secrets Manager secret for DB credentials
- Parameter group (optional but recommended): charset/collation/timezone if needed

Important choices:
- Engine: MySQL (match current app)
- Instance size: small for cost (t-class)
- Backups: enable (even minimal) for realism
- Deletion protection: enabled for “prod”; configurable via context for dev

Exports/outputs:
- `dbEndpointAddress`
- `dbPort`
- `dbName`
- `dbSecretArn`

### 6.3 AppStack
Creates:
- ECR repository (optional if you’re pushing from CI; else create it)
- ECS cluster
- Task definition for web
- Fargate service
- ALB (HTTP->HTTPS redirect + HTTPS listener)
- Target group with health check `/health`
- CloudWatch log group for the service

Also creates:
- **Migration Task Definition** (same image, different command)

Security:
- ALB SG: allow 443 from internet
- ECS SG: allow inbound from ALB SG on container port
- RDS SG: allow inbound from ECS SG on 3306 (configured in DatabaseStack or wired via cross-stack props)

IAM:
- Task execution role: ECR pull + logs (standard)
- Task role: read only the specific Secrets/SSM parameters used (principle of least privilege)

---

## 7) Domain, TLS, OAuth

### 7.1 TLS
- Use **ACM certificate** in the same region as the ALB.
- Use **Route53 hosted zone** for domain (e.g., `adamlacasse.dev`).
- Add `A/AAAA Alias` record to ALB.

### 7.2 OAuth redirect
- Once the ALB domain is stable, set Google OAuth redirect URI to:
  `https://<your-domain>/auth/callback` (or whatever route you use)

---

## 8) Migration / Schema Application Strategy

### 8.1 Why
Your schema contains stored procedures/views; migrations must be repeatable and explicit.

### 8.2 How
Run a one-off ECS task:
- Command: `deploy/migrate.sh`
- Script runs `python app/database/setup_schema.py` (or module form)
- Script pulls connection params from env vars and secrets

### 8.3 When
Deployment workflow (manual or CI step):
1) `cdk deploy NetworkStack DatabaseStack AppStack`
2) Trigger migration task once the DB is reachable:
   - via AWS CLI `ecs run-task` using the migration task definition
   - or via a small helper script in `/infra` that calls AWS SDK
3) Validate: hit `/health`, log in, basic CRUD

**NOTE**: CDK itself does not “run tasks” during deployment; treat migration as a post-deploy step (clean & normal).

---

## 9) Build & Deploy Workflow

### 9.1 Local prerequisites
- AWS CLI configured
- Node 18+ (or 20+)
- Docker
- CDK installed (or use `npx cdk`)

### 9.2 CDK bootstrap
From `infra/`:
- `npm install`
- `npx cdk bootstrap`

### 9.3 Image build/push options
Pick one (agents implement whichever is easier):

Option A (recommended): CI builds/pushes to ECR; CDK references image tag.
Option B: local build/push script.

Required outputs:
- Image in ECR with a tag (e.g., git SHA)

### 9.4 Deploy
- `npx cdk deploy --all`

### 9.5 Run migrations
- `aws ecs run-task ...` (see Runbook section)

---

## 10) Configuration Sources (SSM & Secrets)

### 10.1 Secrets Manager (examples)
- `/northflow/prod/db`:
  - username, password (generated or provided)
- `/northflow/prod/flask_secret_key`
- `/northflow/prod/oauth_client_secret`

### 10.2 SSM Parameter Store (examples)
- `/northflow/prod/flask_env` = `production`
- `/northflow/prod/db_name` = `northflow`
- `/northflow/prod/oauth_client_id` = `...`
- `/northflow/prod/oauth_redirect_uri` = `https://.../auth/callback`

ECS task definition must inject:
- environment values from SSM (plain text)
- secrets from Secrets Manager

---

## 11) Logging & Observability

### v1 requirements
- ECS container logs to CloudWatch Logs (`awslogs` driver)
- Separate log group for migrate task

### Nice-to-have (later)
- ALB access logs to S3
- CloudWatch alarms: 5xx spike, target unhealthy, CPU/mem

---

## 12) Security Requirements

- RDS must not be publicly accessible.
- No secrets in code, no `.env` checked in.
- IAM policies scoped to:
  - `secretsmanager:GetSecretValue` for only required secret ARNs
  - `ssm:GetParameter(s)` for only required paths
- ALB must redirect HTTP->HTTPS.
- Use secure cookies if applicable (Flask session config).

---

## 13) Cost Controls

Be aware:
- NAT Gateway costs can dominate small projects.
- RDS costs are steady.

Controls:
- Use small RDS instance class
- Single NAT (default CDK may create 1 per AZ; configure to 1 if desired)
- Turn off deletion protection in dev
- Use `cdk destroy` for non-prod stacks when not needed

---

## 14) Runbook (Operator Steps)

### 14.1 Validate deployment
- Open `https://<domain>/health`
- Ensure ALB target is healthy
- Check CloudWatch Logs for startup errors

### 14.2 Run migrations (example approach)
Goal: run the migration task definition created by CDK.

Steps:
1) Find cluster name + task definition ARN (from CDK outputs)
2) Run:
   - `aws ecs run-task --cluster <cluster> --task-definition <migrateTaskDefArn> --launch-type FARGATE --network-configuration ...`

Network configuration must use:
- private subnets
- ECS security group
- assignPublicIp: DISABLED (recommended)

### 14.3 Common failure modes
- Tasks can’t reach DB: security group wiring or subnet selection
- Health check failing: wrong port, wrong path, gunicorn not binding `0.0.0.0`
- OAuth redirect mismatch: update Google console and/or env var

---

## 15) Implementation Checklist (for agents)

### App/container changes
- [ ] Add gunicorn dependency
- [ ] Create `deploy/Dockerfile`
- [ ] Create `deploy/entrypoint.sh` (web)
- [ ] Create `deploy/migrate.sh` (migrations)
- [ ] Ensure app factory is importable by gunicorn (e.g., `app:create_app()` pattern)
- [ ] Ensure `/health` exists and returns 200 reliably

### CDK (TypeScript)
- [ ] `infra/` CDK project scaffold
- [ ] `NetworkStack` implemented
- [ ] `DatabaseStack` implemented
- [ ] `AppStack` implemented:
  - [ ] ECS cluster
  - [ ] ALB + HTTPS listener + health check
  - [ ] Task role permissions
  - [ ] Secrets + SSM env injection
  - [ ] Migration task definition

### DNS/TLS
- [ ] Route53 HostedZone lookup
- [ ] ACM cert (DNS validated)
- [ ] Route53 alias record to ALB

### Docs
- [ ] README includes deploy steps and migration step
- [ ] This architecture doc kept up to date

---

## 16) CDK Coding Guidelines

- Keep constructs small and named predictably.
- Use stack props for:
  - `stage` (dev/prod)
  - domain name
  - hosted zone id/name
  - desired image tag
- Put all parameter/secrets path names in `lib/config.ts`.
- Output key ARNs/names needed for run-task and debugging.

---

## 17) Recommended Defaults

- Container port: `8000`
- Gunicorn bind: `0.0.0.0:8000`
- Health check: `/health` every 30s, healthy threshold 2
- Desired count: 1 (for v1)
- RDS: MySQL 8.x compatible
- VPC: 2 AZ, 1 NAT (if configuring for cost)

---

## 18) Future Enhancements (Optional)

- Add CloudWatch alarms and dashboard
- Add autoscaling policies
- Add ALB WAF (light)
- Add CI pipeline: GitHub Actions -> build/push ECR -> cdk deploy -> run migrations
- Add canary / blue-green deploy strategy

---

## 19) Decisions Log (Record changes here)

- CDK language: TypeScript
- Runtime: ECS Fargate behind ALB
- DB: RDS MySQL
- Schema application: one-off ECS migration task
- Secrets: Secrets Manager, config: SSM Parameter Store
