<!-- pymarkdown-disable MD036 -->

# AWS Docker Deployment Plan (Minimum Cost)

> **Status**: Deprecated. The current AWS CDK deployment guide is in
> [DEPLOYMENT_AWS_V2.md](DEPLOYMENT_AWS_V2.md). This file is retained for
> historical reference.

Goal: run the Flask app and MySQL on a single low-cost EC2 box (t4g.micro) with docker-compose. Downtime and backups are acceptable for now.

## Architecture Snapshot

- One EC2 instance (t4g.micro, Amazon Linux 2023, arm64). No ALB, no EIP (use IPv6/IPv4 public DNS).
- Docker + docker-compose running two containers: `web` (Flask) and `db` (MySQL 8.0).
- Secrets in `.env` on the host (fetched once via SSM Parameter Store if desired).
- Ports: 80/443 to the instance; MySQL exposed only to localhost/bridge network.
- Logs: stdout to journal/syslog; optional CloudWatch agent later.

## Prerequisites

- AWS account with t4g.micro eligibility (free tier if within first year).
- Domain optional; otherwise access via public DNS/IP.
- Local workstation with AWS CLI v2 configured.

## Step-by-Step Plan

1) **Prepare Repo for Containers**
   - Add `Dockerfile` for the Flask app (base: `python:3.11-slim` or `amazonlinux:2023` with Python).
   - Add `docker-compose.yml` with `web` + `db` (MySQL 8.0, mount volume for data, init DB via existing schema runner).
   - Add `.dockerignore` to reduce build context.
   - Parameterize app via env vars (`FLASK_ENV=production`, DB creds, SECRET_KEY, GOOGLE OAuth keys).

2) **Harden Default Configs for Container**
   - Ensure `run.py` binds to `0.0.0.0` and uses `$PORT` (fall back to 5000).
   - Confirm config pulls DB host/user/pass from env and points to `db` service name when in compose.
   - Ensure CSRF/session configs already in place; no change needed.

3) **Build and Test Locally**
   - `docker compose up --build` and hit `http://localhost:5000`.
   - Run `docker compose exec web python -m app.database.setup_schema` once to init DB.
   - Run smoke tests: `docker compose exec web pytest` (optional, may need test DB tweaks).

4) **Provision EC2**
   - Launch `t4g.micro` (Amazon Linux 2023, 20GB gp3). Enable IPv6; allow SSH (your IP), HTTP/HTTPS.
   - Attach an IAM role with `AmazonSSMManagedInstanceCore` (optional) and SSM Parameter Store read (if using SSM for secrets).
   - Update security group: open 80/443; keep 22 restricted; block MySQL ingress from internet.

5) **Bootstrap Instance**
   - SSH in; install Docker and docker-compose plugin (`amazon-linux-extras` or package manager).
   - Add your user to `docker` group.
   - (Optional) Install AWS CLI/SSM agent (Amazon Linux 2023 already has SSM agent).

6) **Ship Artifacts to EC2**
   - Option A: git clone repo on the instance and build locally (simple, small codebase).
   - Option B: build/push image to ECR from CI, then `docker pull` on the instance (skip for now to save time/cost).

7) **Configure Secrets/Env on Host**
   - Create `.env` on the instance with DB root/password, app DB creds, SECRET_KEY, OAuth keys, `FLASK_ENV=production`, `PORT=5000`.
   - If using SSM: `aws ssm get-parameter --name <param> --with-decryption` to populate the file.

8) **Deploy Containers**
   - `docker compose up -d --build`.
   - Initialize DB: `docker compose exec web python -m app.database.setup_schema`.
   - Verify app: `curl http://localhost:5000/health`.

9) **Make It Reachable**
   - For HTTP: open port 80 in SG and use instance public DNS.
   - For HTTPS (optional initial): run certbot on host and terminate TLS with nginx reverse proxy container, or defer until traffic exists.

10) **Basic Ops**

- Restart on boot: create a `systemd` service that runs `docker compose up -d` in the repo directory.
- Logs: `docker compose logs -f web` / `db`. Add CloudWatch agent later if needed.
- Backups (optional later): nightly `mysqldump` to local file or S3; acceptable to skip now.

## Future Upgrades (when/if traffic arrives)

- Move DB to RDS MySQL (db.t4g.micro) for durability.
- Add TLS termination (ALB or nginx + certbot).
- CI/CD: GitHub Actions builds image to ECR; SSM Run Command triggers `docker compose pull && up -d`.
- Monitoring: CloudWatch agent, alarms on CPU/status checks/health endpoint.
