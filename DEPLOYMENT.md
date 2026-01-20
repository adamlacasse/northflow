# NorthFlow Deployment Documentation

> **Status**: Legacy (Railway). The current AWS CDK deployment guide is in
> [DEPLOYMENT_AWS_V2.md](DEPLOYMENT_AWS_V2.md). This file is retained for
> historical reference.

## Current Deployment Status

NorthFlow is currently deployed to **Railway** with a **MySQL 8.0** database instance.

### Infrastructure Overview

- **Platform**: [Railway](https://railway.app/)
- **Application Service**: Flask app running on Railway
- **Database Service**: MySQL 8.0 instance on Railway
- **Health Check**: `/health` endpoint (120-second timeout)
- **Restart Policy**: On failure, max 3 retries

### Railway Configuration

The deployment is configured in [railway.toml](railway.toml):

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python run.py"
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### Environment Variables (Railway)

The following environment variables must be set in the Railway project settings:

- `FLASK_ENV` – Set to `production`
- `DB_HOST` – Railway MySQL instance hostname
- `DB_PORT` – MySQL port (typically 3306)
- `DB_USER` – MySQL username
- `DB_PASSWORD` – MySQL password
- `SECRET_KEY` – Flask secret key (use a strong random value)
- `PORT` – Application port (Railway sets this, but can be overridden)

**Note**: Do NOT commit `.env` files. All secrets must be set in Railway's environment variable UI.

### Database Setup on Railway

The MySQL instance needs the schema initialized on first deployment:

1. SSH into Railway or use Railway CLI to run a one-time job:

   ```bash
   railway run python -m app.database.setup_schema
   ```

2. This executes [app/database/setup_schema.py](app/database/setup_schema.py), which:
   - Drops and recreates the `northflow` database
   - Runs the schema from [app/database/schema.sql](app/database/schema.sql)
   - Seeds the database with initial data

### Health Checks

The `/health` endpoint at [app/routes/main.py](app/routes/main.py) returns:

- **200 OK** with `{"status": "healthy", "database": "connected"}` on success
- **503 Service Unavailable** with `{"status": "unhealthy", "error": "..."}` on DB connection failure

Railway monitors this endpoint every 30 seconds (configurable). Failed health checks trigger restart.

### Deployment Workflow

1. **Push to main/deploy branch** (or configured trigger in Railway)
2. Railway **builds** the app using nixpacks builder
3. Railway **runs** `python run.py` to start the Flask app
4. Railway **monitors** `/health` endpoint
5. On success, the app is **live**

### Logs & Monitoring

- View logs in Railway dashboard or via Railway CLI
- Check health endpoint: `curl https://<railway-app-url>/health`
- Monitor database connectivity issues via Flask error logs

### Scaling & Limits

**Current (Course Project)**:

- Single dyno/service instance
- Shared MySQL instance
- No load balancing or auto-scaling

**For Production Readiness** (see [TODO.md](TODO.md) items 22, 23, 25):

- Add monitoring & alerting (Prometheus/Grafana or Railway's built-in)
- Consider read replicas for high-traffic scenarios
- Implement auto-scaling policies
- Add CDN for static assets
- Setup backup retention policies

### Known Limitations

1. **No user authentication yet** – App currently uses DB credential login (see [TODO.md](TODO.md) item 4)
2. **No connection pooling** – Uses single connections per request (see [TODO.md](TODO.md) item 6)
3. **No rate limiting** – Open to abuse (see [TODO.md](TODO.md) item 10)
4. **Basic error handling** – No error tracking or centralized logging (see [TODO.md](TODO.md) items 8, 9)

### Next Steps

Before scaling production traffic:

1. Implement proper authentication (TODO item 4)
2. Add security hardening (TODO items 1–3, 5, 10)
3. Setup monitoring & alerting (TODO item 22)
4. Add connection pooling (TODO item 6)
5. Create deployment runbooks (TODO item 23)

See [TODO.md](TODO.md) for the full production roadmap.

### Rollback & Disaster Recovery

**Current process**:

1. Revert commit on main branch
2. Push to trigger a new Railway build
3. Railway deploys the previous code
4. Database schema stays at last migration (no automatic rollback)

**For production readiness**:

- Implement database migrations with rollback support (TODO item 11)
- Document RTO/RPO targets (TODO item 21)
- Test recovery procedures regularly
