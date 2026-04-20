# NorthFlow - AI Coding Agent Instructions

## Project Overview

NorthFlow is a Flask-based mindfulness/gratitude check-in app built as the first MVP for a CSC-6302 Database Principles course project. The project emphasizes a clean DAL pattern, multi-dialect linting, and environment-based configuration.

## Architecture & Key Components

### Application Factory Pattern

- Entry point: `run.py` → `create_app(config_name)` in `app/__init__.py`
- Config determined by `FLASK_ENV` environment variable (defaults to `development`)
- Configs defined in `config.py`: `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`
- All configs share the same `northflow` database; multi-environment support is future work
- App factory initializes CSRF protection, rate limiting, OAuth, and security headers

### Authentication & Authorization (`app/routes/auth.py` + `app/auth.py`)

- **OAuth 2.0**: Third-party authentication via Google only (uses `authlib`)
- **No password storage**: Users authenticate through Google OAuth
- **Auto-registration**: New users are automatically created on first login
- **Session management**: Sessions are persistent (`session.permanent = True`) with 1-hour timeout
- **`@login_required` decorator**: Protects all routes except `/health`
- **User context**: `session['user_id']` set after OAuth callback; `_get_current_user()` reads from session
- **DAL**: `app/dal/oauth_users.py` handles OAuth user CRUD (get by OAuth ID, get by email, create user, update last login)

### Database Layer (`app/dal/database_connection.py`)

- **`DatabaseConnection`**: Primary DAL class wrapping `mysql-connector-python`
  - Always returns dictionary cursors for consistent JSON-like results
  - Methods: `execute_query()`, `call_procedure()`, `commit()`, `close()`
  - Raises custom `DatabaseError` on failures with detailed logging
- **Connection pattern**: Instantiate → execute → close
- **Database credentials**: Always loaded from environment config (`Config.DB_HOST`, etc.), never from session
- **Stored procedures**: Use `call_procedure(proc_name, params)` for CRUD operations defined in `schema.sql`

### Database Schema (`app/database/schema.sql`)

- Five main tables: `users` (with OAuth fields), `user_questions`, `checkins`, `answers`, `oauth_users`
- **User table fields**: `id`, `email` (UNIQUE), `first_name`, `last_name`, `oauth_provider`, `oauth_id`, `created_at`, `last_login`
- Includes stored procedures for `user_questions` CRUD (`add_user_question`, `update_user_question`, `delete_user_question`)
- Seed data includes one Demo User (ID 1) for bootstrapping
- Initialize with: `invoke execute-schema` (runs `app/database/setup_schema.py`)

### Routing

- **Authentication blueprint** (`app/routes/auth.py`):
  - `GET /auth/login`: Show OAuth login page with Google sign-in button
  - `GET /auth/login/google`: Redirect to Google OAuth
  - `GET /auth/callback/google`: Handle OAuth callback (auto-register or login user)
  - `GET /auth/logout`: Clear session and redirect to login
  - Exports `login_required` decorator used by all protected routes
  
- **Main blueprint** (`app/routes/main.py`) - ALL routes protected by `@login_required` except `/health`:
  - `GET /`: Entry route, redirects to questions page
  - `GET /questions`: Lists current user's questions
  - `POST /questions/create`: Creates a user question (stored procedure)
  - `POST /questions/<question_id>/update`: Updates a user question
  - `POST /questions/<question_id>/delete`: Deletes a user question
  - `GET /checkins`: Lists current user's check-ins
  - `POST /checkins/create`: Creates a check-in for current user
  - `GET /checkins/<id>`: Check-in detail page
  - `POST /checkins/<id>/update`: Updates check-in notes
  - `POST /checkins/<id>/delete`: Deletes check-in and answers
  - `POST /checkins/<id>/answers/<question_id>/save`: Saves/updates answer
  - `POST /checkins/<id>/answers/<question_id>/delete`: Deletes answer
  - `GET /summary`: Reads aggregated rows from `user_daily_summary` view (filtered to current user)
  - `GET /health`: Returns JSON health status (200/503, no auth required)

- **Import pattern**:
  - From auth: `from app.routes.auth import login_required`
  - From DAL: `from app.dal import DatabaseConnection, DatabaseError`
  - OAuth DAL: `from app.dal.oauth_users import create_oauth_user, get_user_by_oauth, etc.`

## Developer Workflows

### Environment Setup

1. Create `.env` file with: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`, `FLASK_ENV`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
2. `pip install -r requirements.txt` (installs package + dev tools from `pyproject.toml`)
3. `invoke execute-schema` to create database and tables
4. Register app with [Google Cloud Console](https://console.cloud.google.com) to get OAuth credentials

### Running the App

- `python run.py` → serves on `0.0.0.0:5000`
- Navigate to `http://localhost:5000` → redirects to `/auth/login`
- Click "Sign in with Google" to authenticate
- After login, access all features (questions, check-ins, summary)
- Test health: `curl http://localhost:5000/health` (no auth required)

### Linting (Critical Workflow)

- **Multi-dialect linting**: Python (Ruff), SQL (SQLFluff), HTML/Jinja2 (djlint)
- `invoke lint` → runs all three with auto-fix
- Granular: `invoke lint-python`, `invoke lint-sql`, `invoke lint-html`
- All tasks defined in `tasks.py` using `invoke` library
- Ruff config in `pyproject.toml`: line-length 88, Python 3.8+

### Testing

- Run: `pytest tests/` (requires active DB connection per `.env`)
- Tests use module-scoped `db_connection` fixture for efficiency
- Test pattern: Load `.env` explicitly via `load_dotenv()` in test file
- Example: `test_connection.py` verifies DAL methods, connection lifecycle, error handling

## Project-Specific Conventions

### Import Organization

- Config imports: `from config import Config, config` (note: lowercase `config` dict)
- DAL imports: `from app.dal import DatabaseConnection, DatabaseError`
- Package structure exports in `__init__.py` files (see `app/dal/__init__.py`)

### Error Handling

- Always wrap DB operations in try/except and raise `DatabaseError` with context
- Log errors before raising: `logging.error(f"Query failed with error: {e}")`
- Health endpoint demonstrates error handling pattern returning 503 on DB failure

### Configuration Pattern

- All configs inherit from base `Config` class
- Environment vars loaded via `python-dotenv` at module level in `config.py`
- Access config in app via: `app.config.from_object(config[config_name])`

### SQL & Database

- MySQL 8.0+ dialect required for SQLFluff
- Use stored procedures for CRUD on `user_questions`
- Read-only/lookup queries (e.g., listing users and reading the summary view) may use parameterized SELECTs via the DAL
- Schema drops and recreates `northflow` database on initialization
- Foreign keys use `ON DELETE CASCADE` consistently

## Key Files Reference

- **DAL patterns**: `app/dal/database_connection.py` (DatabaseConnection class)
- **Blueprint registration**: `app/__init__.py` (create_app factory)
- **Health check example**: `app/routes/main.py` (/health endpoint)
- **Test fixtures**: `tests/test_connection.py` (module-scoped DB fixture)
- **Task automation**: `tasks.py` (invoke commands for lint/schema)
- **Schema with seed data**: `app/database/schema.sql` (includes stored procs)

## Documentation scope

- README is human-facing and should track the current state of the application so others can run it locally; avoid embedding todos or historical notes there.

## Extended Context

- **`docs` folder**: Contains larger application context and documentation that continues to be iterated on

## DO NOTs

- Don't bypass `DatabaseConnection` class for direct mysql-connector usage
- Don't create environment-specific databases (all envs use `northflow`)
- Don't skip linting—this project enforces Python, SQL, AND HTML linting
- Don't forget `.env` file—app will fail on missing DB credentials and OAuth secrets
- Don't write SQL directly in routes; use DAL methods or stored procedures
- Don't use `{{ csrf_token() }}` alone in templates; always wrap in hidden input: `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- Don't forget to mark sessions as persistent in OAuth callbacks: `session.permanent = True`

## Deployment

*“Authoritative deployment documentation lives in `docs/DEPLOYMENT_ACTIVE.md`.”*
