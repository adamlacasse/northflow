# NorthFlow

A mindfulness/gratitude check-in app, created as the final project for
CSC-6302 Database Principles

## Overview

NorthFlow currently provides:

- A Flask app factory (`app/__init__.py`) that wires configuration,
  routes, and assets.
- A `DatabaseConnection` helper (`app/models/dal.py`) that wraps
  `mysql-connector-python` and standardizes error handling through
  `DatabaseError`.
- UI flows for database login, `user_questions` CRUD via stored
  procedures, and a daily summary view over the `user_daily_summary`
  view.
- A simple landing page plus a `/health` endpoint that validates the
  database connection at runtime.
- A MySQL schema (`app/database/schema.sql`) that captures users,
  custom questions, check-ins, answers, and the `user_daily_summary`
  aggregation view.

While the database schema anticipates full CRUD features, the live UI
is intentionally minimal so the focus can remain on the DAL, routing,
and deployment pipeline.

## Architecture at a Glance

- **Application entry point**: `run.py` creates the Flask app using the
  `FLASK_ENV` (defaults to `development`) and serves it on
  `0.0.0.0:5000`.
- **Configuration**: `config.py` loads environment variables via
  `python-dotenv` and defines `DevelopmentConfig`, `TestingConfig`, and
  `ProductionConfig` classes. All rely on the `northflow` database by
  default.
- **Blueprints**: `app/routes/main.py` exposes `GET /` (landing page),
  `GET/POST /login` (DB connection gate), `GET /questions` with
  supporting CRUD endpoints for `user_questions`, `GET /summary` for
  the daily aggregation view, and `GET /health` (DB connectivity check
  returning JSON 200/503).
- **Templates & static assets**: `app/templates` plus `app/static/{css,
  js,images}` provide the UI shell; styles and scripts are deliberately
  minimal and easy to extend.
- **Data layer**: `DatabaseConnection` supplies helpers for
  `execute_query`, stored procedures, commits, and teardown with
  consistent logging. Business logic lives in `app/services`, including
  `user_questions` (CRUD + listing via stored procedures) and `summary`
  (daily reporting via a stored procedure wrapper over the
  `user_daily_summary` view).
- **Testing**: `tests/test_connection.py` exercises the DAL, verifying
  that connections, queries, and error handling behave as expected.

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- `pip`

### Installation

```bash
git clone https://github.com/adamlacasse/northflow.git
cd northflow

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt          # installs app plus tooling extras
```

### Configuration

Create a `.env` file in the project root (It will be loaded automatically
by `config.py`):

```env
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
SECRET_KEY=change-me
FLASK_ENV=development
```

### Database Initialization

Use the project helper to apply the schema with the credentials in your
`.env` file:

```bash
invoke execute-schema
```

The command runs `app/database/setup_schema.py`, creating the
`northflow` database plus the `users`, `user_questions`, `checkins`, and
`answers` tables. If you prefer to run the SQL manually, you can still
execute `mysql -u $DB_USER -p < app/database/schema.sql`.

### Stored Routines

`schema.sql` includes stored procedures for adding/updating/deleting
`user_questions` to demonstrate CRUD patterns in MySQL.

## Running the App

```bash
python run.py
```

Visit `http://localhost:5000` for the landing page.

If you are not connected yet, `/` will redirect you to `/login`.

Login flow (DB connection required for data):

- Go to `/login` and enter DB host, port, user, and password
  (database name is fixed to `northflow`).
- On success, you will be redirected to `/questions`.
- Manage custom prompts at `/questions` (add/update/delete via stored
  procedures with live refresh).
- View aggregated daily stats at `/summary`, with optional user and
  date filters sourced from the `user_daily_summary` view.

Health endpoint (requires DB connectivity):

```bash
curl http://localhost:5000/health
# -> {"status": "healthy", "database": "connected"}
```

## Tooling & Quality Gates

- `invoke lint` – run Ruff (Python), SQLFluff (SQL), and djlint (HTML/
  Jinja) with auto-fix enabled.
- `invoke lint-python` – Python-only lint/format.
- `invoke lint-sql` – SQL formatting/linting for `app/database`.
- `invoke lint-html` – Template lint/format pass via djlint.
- `pytest tests/` – runs the DAL test suite (requires a reachable DB
  defined by your `.env`).

## Project Structure

```text
app/
├── __init__.py          # Flask app factory
├── database/
│   └── schema.sql       # MySQL schema bootstrap
│   └── setup_schema.py  # Schema application helper
├── models/
│   ├── __init__.py
│   └── dal.py           # DatabaseConnection + DatabaseError
├── routes/
│   ├── __init__.py
│   └── main.py          # Landing, login, questions CRUD, summary, health
├── static/
│   ├── css/style.css    # Base styles
│   ├── js/main.js       # Placeholder JS hooks
│   └── images/
└── templates/
  ├── base.html        # Layout shell
  ├── index.html       # Hero + features copy
  ├── questions.html   # user_questions CRUD UI
  └── summary.html     # daily aggregation view
app/services/
├── user_questions.py    # Stored-proc CRUD helpers
└── summary.py           # View reader for user_daily_summary
config.py                # Environment-aware settings
run.py                   # App entry point
tasks.py                 # Invoke task helpers
tests/test_connection.py # DAL regression tests
```

## Future Enhancements

- Add authentication and session management on top of the current UI
  shell.
- Expand the frontend with dashboards fed by DAL metrics/APIs.

## License

Released under the MIT License. See `LICENSE` for details.
