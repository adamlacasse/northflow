# NorthFlow

A mindfulness/gratitude check-in app, created as the final project for
CSC-6302 Database Principles

## Overview

NorthFlow currently provides:

- A Flask app factory (`app/__init__.py`) that wires configuration,
  routes, and assets.
- A `DatabaseConnection` helper (`app/dal/database_connection.py`) that wraps
  `mysql-connector-python` and standardizes error handling through
  `DatabaseError`.
- A MySQL schema (`app/database/schema.sql`) that captures users,
  custom questions, check-ins, answers, and the `user_daily_summary`
  aggregation view.
- Full CRUD operations for managing check-ins and answers with a clean
  web UI for creating check-ins, recording answers, and viewing historical data.

## Advanced Feature: Aggregated Daily Summary

**This project's advanced feature** is a multi-table aggregation view that provides analytical reporting over user check-in data.

- **Database implementation**: The `user_daily_summary` VIEW aggregates data
from `users`, `checkins`, and `answers` tables using `COUNT()`, `AVG()`, `MIN()`, and `MAX()` functions grouped by user and date.
- **Stored procedure wrapper**: `list_daily_summary` stored procedure wraps the
view and accepts optional filter parameters (user ID, start date, end date).
- **UI implementation**: The `/summary` page provides a filterable interface to
view aggregated statistics including total check-ins, answer counts, and score summaries per user per day.

This feature demonstrates meaningful data summarization beyond basic CRUD operations, as required by the project rubric.

## Architecture at a Glance

- **Application entry point**: `run.py` creates the Flask app using the
  `FLASK_ENV` (defaults to `development`) and serves it on
  `0.0.0.0:5000`.
- **Configuration**: `config.py` loads environment variables via
  `python-dotenv` and defines `DevelopmentConfig`, `TestingConfig`, and
  `ProductionConfig` classes. All rely on the `northflow` database by
  default.
- **Single-user perspective**: The app is configured for single-user mode
  with a hardcoded Demo User (ID 1). All routes auto-filter to the current user.
  User authentication system is planned (see [TODO.md](TODO.md#security)).
- **Blueprints**: `app/routes/main.py` exposes:
  - `GET /` – Landing page with mindfulness check-in interface
  - `GET /questions` – Manage your custom check-in questions (CRUD via stored procedures)
  - `GET /checkins` – View and filter your historical check-ins
  - `POST /checkins/create` – Create a new check-in session
  - `GET /checkins/<id>` – Answer your custom questions for a check-in
  - `POST /checkins/<id>/update` – Update check-in notes
  - `GET /summary` – View aggregated daily statistics (mood, scores, trends)
  - `POST /checkins/<id>/delete` – Delete check-in and all answers
  - `POST /checkins/<id>/answers/<question_id>/save` – Save/update answer
  - `POST /checkins/<id>/answers/<question_id>/delete` – Remove answer
  - `GET /summary` – View aggregated daily check-in statistics with filters
  - `GET /health` – DB connectivity check (returns JSON 200/503)
- **Templates & static assets**: `app/templates` plus `app/static/{css,
  js,images}` provide the UI shell; styles and scripts are deliberately
  minimal and easy to extend.
- **Data layer**: The DAL lives in `app/dal`. `DatabaseConnection`
  supplies helpers for stored procedures, commits, and teardown with
  consistent logging. Business logic lives in `app/services`, including:
  - `user_questions` – CRUD + listing via stored procedures
  - `checkins` – Check-in CRUD operations
  - `answers` – Answer CRUD operations
  - `summary` – Daily reporting via a stored procedure wrapper over the
    `user_daily_summary` view
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
DB_PORT=3306
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
- **Manage custom prompts** at `/questions` (add/update/delete via stored
  procedures with live refresh).
- **Create and manage check-ins** at `/checkins` – select a user to view
  their check-ins, create new ones, and record answers to their custom questions.
  Question-type aware forms handle text, numeric, 1-5 scales, and boolean responses.
- **View aggregated daily stats** at `/summary`, with optional user and
  date filters sourced from the `user_daily_summary` view.

Health endpoint (requires DB connectivity):

```bash
curl http://localhost:5000/health
# -> {"status": "healthy", "database": "connected"}
```

`/health` uses the active session connection if you have already connected via
`/login`. Otherwise, it falls back to the `.env` database settings.

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
├── dal/
│   ├── __init__.py
│   ├── database_connection.py  # DatabaseConnection + DatabaseError
│   ├── user_questions.py       # User questions domain DAL
│   ├── checkins.py             # Check-in domain DAL (CRUD via stored procedures)
│   ├── answers.py              # Answer domain DAL (CRUD via stored procedures)
│   └── summary.py              # Daily summary domain DAL
├── database/
│   ├── schema.sql       # MySQL schema with 10+ stored procedures/views
│   └── setup_schema.py  # Schema application helper
├── routes/
│   ├── __init__.py
│   └── main.py
├── services/
│   ├── __init__.py
│   ├── user_questions.py       # Business logic for user questions
│   ├── checkins.py             # Business logic for check-in CRUD
│   ├── answers.py              # Business logic for answer CRUD
│   └── summary.py              # Business logic for daily summary
├── static/
│   ├── css/style.css    # Base styles (285 lines, no inline styles)
│   ├── js/main.js       # Placeholder JS hooks
│   └── images/
└── templates/
  ├── base.html        # Layout shell with navigation
  ├── index.html       # Hero + features copy
  ├── login.html       # DB connection form
  ├── questions.html   # user_questions CRUD UI
  ├── checkins.html    # Check-in list, filter, and create form
  ├── checkin_detail.html # Check-in detail with dynamic answer forms
  └── summary.html     # Daily aggregation view with filters
config.py                # Environment-aware settings
run.py                   # App entry point
tasks.py                 # Invoke task helpers
tests/test_connection.py # DAL regression tests
```

## License

Released under the MIT License. See `LICENSE` for details.
