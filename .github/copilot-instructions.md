# NorthFlow - AI Coding Agent Instructions

## Project Overview
NorthFlow is a Flask-based mindfulness/gratitude check-in app built as the first MVP for a CSC-6302 Database Principles course project. The project emphasizes a clean DAL pattern, multi-dialect linting, and environment-based configuration. The UI is intentionally minimal—focus is on database interaction, error handling, and deployment readiness. See `.agent/AGENT_CONTEXT.md` for the course rubric and deliverable constraints.

Advanced feature planning is documented in [ADVANCED_FEATURE.md](../.agent/ADVANCED_FEATURE.md).

## Architecture & Key Components

### Application Factory Pattern
- Entry point: `run.py` → `create_app(config_name)` in `app/__init__.py`
- Config determined by `FLASK_ENV` environment variable (defaults to `development`)
- Configs defined in `config.py`: `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`
- All configs share the same `northflow` database; multi-environment support is future work

### Database Layer (`app/dal/database_connection.py`)
- **`DatabaseConnection`**: Primary DAL class wrapping `mysql-connector-python`
  - Always returns dictionary cursors for consistent JSON-like results
  - Methods: `execute_query()`, `call_procedure()`, `commit()`, `close()`
  - Raises custom `DatabaseError` on failures with detailed logging
- **Connection pattern**: Instantiate → execute → close (see `/health` endpoint in `app/routes/main.py`)
- **Stored procedures**: Use `call_procedure(proc_name, params)` for CRUD operations defined in `schema.sql`

### Database Schema (`app/database/schema.sql`)
- Four main tables: `users`, `user_questions`, `checkins`, `answers`
- Includes stored procedures for `user_questions` CRUD (`add_user_question`, `update_user_question`, `delete_user_question`)
- Schema includes seed data with user variables (`@avery_id`, `@jordan_id`, etc.)
- Initialize with: `invoke execute-schema` (runs `app/database/setup_schema.py`)

### Routing (`app/routes/main.py`)
- Single blueprint: `main` registered in app factory
- Routes:
  - `GET /`: Landing page rendering `app/templates/index.html`
  - `GET/POST /login`: DB connection gate (host/user/password/port) stored in session
  - `GET /logout`: Clears DB session credentials
  - `GET /questions`: Lists users + questions
  - `POST /questions/create`: Creates a user question (stored procedure)
  - `POST /questions/<question_id>/update`: Updates a user question (stored procedure with OUT success flag)
  - `POST /questions/<question_id>/delete`: Deletes a user question (stored procedure)
  - `GET /summary`: Reads aggregated rows from the `user_daily_summary` view with optional filters
  - `GET /health`: Returns JSON `{"status": "healthy", "database": "connected"}` (200) or `{"status": "unhealthy", "error": "..."}` (503)
- Import pattern: `from app.dal import DatabaseConnection, DatabaseError`

## Developer Workflows

### Environment Setup
1. Create `.env` file with: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`, `FLASK_ENV`
2. `pip install -r requirements.txt` (installs package + dev tools from `pyproject.toml`)
3. `invoke execute-schema` to create database and tables

### Running the App
- `python run.py` → serves on `0.0.0.0:5000`
- Test health: `curl http://localhost:5000/health`

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
- **`.agent` folder**: Contains larger application context and documentation that continues to be iterated on

## DO NOTs
- Don't bypass `DatabaseConnection` class for direct mysql-connector usage
- Don't create environment-specific databases (all envs use `northflow`)
- Don't skip linting—this project enforces Python, SQL, AND HTML linting
- Don't forget `.env` file—app will fail on missing DB credentials
- Don't write SQL directly in routes; use DAL methods or stored procedures
