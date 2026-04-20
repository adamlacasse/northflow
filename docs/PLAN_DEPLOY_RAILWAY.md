# Plan: Deploy NorthFlow on Railway

> **Status:** Ready for execution
> **Created:** 2026-04-03
> **Purpose:** Deploy the Flask web service and MySQL database on Railway.
> **Cost estimate:** $0–8/month (Hobby plan: $5/month subscription with $5 credit;
> a low-traffic hobby app typically stays within the credit)

---

## Why Railway

- Runs Docker containers natively (the existing `deploy/Dockerfile` works as-is)
- Offers managed MySQL 8.0 as a first-class service
- Internal private networking between services (no public DB exposure)
- Sets `PORT` automatically; the app already reads `PORT` from env
- $5/month Hobby plan with $5 usage credit covers light hobby traffic
- Zero stored-procedure migration — real MySQL, full compatibility

---

## Prerequisites

Before starting:

- A Railway account (<https://railway.app>) on the Hobby plan ($5/month)
- The GitHub repo (`adamlacasse/northflow`) accessible from Railway
- Google and GitHub OAuth credentials (existing ones; redirect URIs will change)
- Cloudflare DNS access for `adamlacasse.dev` (if using a custom domain)

---

## Step 1: Create the Railway Project

1. Log in to [railway.app](https://railway.app)
2. Click **New Project**
3. Choose **Deploy from GitHub repo** and select `adamlacasse/northflow`
4. Railway will detect the root `Dockerfile` — we need to override this (see Step 3)

---

## Step 2: Add a MySQL Service

1. Inside the project, click **New** → **Database** → **MySQL**
2. Railway provisions a MySQL 8.0 instance and exposes these variables
   to any linked service:

   | Railway variable | Value |
   |-----------------|-------|
   | `MYSQLHOST` | Private hostname (e.g., `mysql.railway.internal`) |
   | `MYSQLPORT` | Port (typically `3306`) |
   | `MYSQLUSER` | `root` |
   | `MYSQLPASSWORD` | Auto-generated |
   | `MYSQLDATABASE` | `railway` |
   | `MYSQL_URL` | Full connection string |

3. **Rename the default database to `northflow`** (optional but cleaner):
   - Go to the MySQL service → **Data** tab → run:

     ```sql
     CREATE DATABASE IF NOT EXISTS northflow;
     ```

   - Or leave it as `railway` and set `DATABASE=railway` in the web
     service variables (Step 3). The app's `config.py` reads
     `Config.DATABASE` which defaults to `northflow`.

---

## Step 3: Configure the Web Service

### 3.1 Set the Dockerfile path

Railway detected the root `Dockerfile` (development image). Override it to
use the production image:

1. Go to the web service → **Settings**
2. Under **Build**, set **Dockerfile Path** to `deploy/Dockerfile`

### 3.2 Set environment variables

Go to the web service → **Variables** tab and add:

| Variable | Value | Notes |
|----------|-------|-------|
| `DB_HOST` | `${{MySQL.MYSQLHOST}}` | Railway variable reference |
| `DB_PORT` | `${{MySQL.MYSQLPORT}}` | Railway variable reference |
| `DB_USER` | `${{MySQL.MYSQLUSER}}` | Railway variable reference |
| `DB_PASSWORD` | `${{MySQL.MYSQLPASSWORD}}` | Railway variable reference |
| `DATABASE` | `northflow` | Or `railway` if you skipped the rename |
| `SECRET_KEY` | *(generate one)* | `python3 -c 'import secrets; print(secrets.token_hex(32))'` |
| `FLASK_ENV` | `production` | Selects `ProductionConfig` |
| `GOOGLE_CLIENT_ID` | *(your value)* | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | *(your value)* | From Google Cloud Console |
| `GITHUB_CLIENT_ID` | *(your value)* | From GitHub Developer Settings |
| `GITHUB_CLIENT_SECRET` | *(your value)* | From GitHub Developer Settings |

**Note on `DATABASE`:** The app's `config.py` hardcodes `DATABASE = "northflow"`.
If you want to use Railway's default database name (`railway`), you will need a
one-line config change — see Step 7 below. Otherwise, create the `northflow`
database in Step 2.

### 3.3 Health check

In the web service **Settings**:

- Set **Health Check Path** to `/health`
- Railway will wait for a 200 before routing traffic

---

## Step 4: Bootstrap the Database (One Time Only)

The database needs its schema, tables, and stored procedures. Run this once
after the MySQL service is live.

**Option A — Railway CLI (recommended):**

```bash
railway run --service web -- /app/deploy/entrypoint.sh migrate
```

With `MIGRATE_MODE=schema` set as a temporary variable:

```bash
MIGRATE_MODE=schema railway run --service web -- /app/deploy/migrate.sh
```

**Option B — From the Railway console:**

1. Go to the web service → **Settings** → temporarily change the
   **Start Command** to:

   ```
   MIGRATE_MODE=schema /app/deploy/migrate.sh
   ```

2. Trigger a redeploy. The container will run the destructive bootstrap
   and exit.
3. **Immediately revert** the start command (remove the override so it
   falls back to the Dockerfile's `ENTRYPOINT`/`CMD`).

After bootstrap, the safe `apply_schema_objects` step runs automatically
via `entrypoint.sh` on every deploy — but currently it does not. See
Step 6 for adding this.

---

## Step 5: Deploy

1. Push to your GitHub repo (or trigger a manual deploy in Railway)
2. Railway builds the `deploy/Dockerfile`, injects env vars, and starts
   the container
3. The entrypoint runs gunicorn on the `PORT` Railway assigns
4. The `/health` endpoint confirms DB connectivity and routine presence

---

## Step 6: Add Automatic Schema Object Migration

The `entrypoint.sh` currently goes straight to gunicorn without running
`apply_schema_objects`. To ensure stored procedures/views are always
current on every deploy, update `deploy/entrypoint.sh`:

**Current:**

```sh
if [ "$MODE" = "web" ]; then
  CONFIG_NAME=${FLASK_ENV:-production}
  exec gunicorn ...
```

**Updated:**

```sh
if [ "$MODE" = "web" ]; then
  echo "Applying schema objects..."
  MIGRATE_MODE=objects /app/deploy/migrate.sh
  CONFIG_NAME=${FLASK_ENV:-production}
  exec gunicorn ...
```

This is safe and repeatable — it runs `DROP ... IF EXISTS` + `CREATE ...`
for all procedures and views before starting the web server.

---

## Step 7: Make `DATABASE` Configurable (Optional)

If you want to use Railway's default `railway` database name instead of
creating a `northflow` database, make this one-line change in `config.py`:

```python
# Before
DATABASE = "northflow"

# After
DATABASE = os.getenv("DATABASE", "northflow")
```

This lets the env var override the default while keeping local dev unchanged.

---

## Step 8: Custom Domain (Cloudflare)

1. In Railway, go to the web service → **Settings** → **Networking** →
   **Custom Domain** → enter your domain (e.g., `northflow.adamlacasse.dev`)
2. Railway gives you a CNAME target (e.g., `your-service.up.railway.app`)
3. In Cloudflare DNS, add:

   | Type | Name | Target | Proxy |
   |------|------|--------|-------|
   | CNAME | `app` | `your-service.up.railway.app` | DNS only (grey cloud) |

4. Railway handles TLS automatically (no certificate management needed)
---

## Step 9: Update OAuth Redirect URIs

After the custom domain is live:

1. **Google Cloud Console** → APIs & Services → Credentials →
   your OAuth client → add authorized redirect URI:
   `https://northflow.adamlacasse.dev/auth/callback/google`

2. **GitHub Developer Settings** → OAuth Apps → your app →
   update callback URL:
   `https://northflow.adamlacasse.dev/auth/callback/github`

---

## Step 10: Verify

After deployment, confirm:

- [ ] `https://northflow.adamlacasse.dev/health` returns 200
- [ ] Google OAuth login works end-to-end
- [ ] GitHub OAuth login works end-to-end
- [ ] Creating a question, check-in, and answer all succeed
- [ ] The `/summary` page loads with data

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Railway Hobby plan | $5/month (includes $5 usage credit) |
| MySQL service (idle/light) | ~$1–3/month of credit |
| Web service (light traffic) | ~$1–2/month of credit |
| **Typical total** | **$5–8/month** |

The web service sleeps when idle (configurable). For a hobby app with a few
users, you will likely stay within or just above the $5 credit most months.

---

## Code Changes Summary

| Action | File | Reason |
|--------|------|--------|
| **EDIT** | `deploy/entrypoint.sh` | Add `apply_schema_objects` before gunicorn |
| **EDIT** | `config.py` | Make `DATABASE` configurable via env var (optional) |
| **EDIT** | `docs/DEPLOYMENT_ACTIVE.md` | Update to reflect Railway deployment |
| **EDIT** | `docs/DECISIONS.md` | Update deployment runtime decision |

No changes needed to application code, routes, DAL, templates, or tests.
