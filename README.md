# NorthFlow

A mindfulness/gratitude check-in app, created as the final project for
CSC-6302 Database Principles

> **Note for AI agents:** See [TODO.md](TODO.md) for open questions and code/doc alignment tasks.

## Overview

NorthFlow currently provides:

- **OAuth 2.0 Authentication**: Secure login with Google OAuth (no password storage)
- A Flask app factory (`app/__init__.py`) that wires configuration,
  routes, and assets with CSRF protection, rate limiting, and security headers.
- A `DatabaseConnection` helper (`app/dal/database_connection.py`) that wraps
  `mysql-connector-python` and standardizes error handling through
  `DatabaseError`.
- A MySQL schema (`app/database/schema.sql`) that captures users,
  custom questions, check-ins, answers, and the `user_daily_summary`
  aggregation view.
- Full CRUD operations for managing check-ins and answers with a clean
  web UI for creating check-ins, recording answers, and viewing historical data.
- Session-based authentication with protected routes and automatic user context.

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
- **Authentication**: OAuth 2.0 with Google (via `authlib`). Users auto-register
  on first login. Sessions are permanent with 1-hour timeout. All app routes except
  `/auth/*` and `/health` require authentication via `@login_required`.
- **Blueprints**:
  - **`app/routes/auth.py`** exposes:
    - `GET /auth/login` – OAuth login page with Google sign-in button
    - `GET /auth/login/google` – Redirect to Google OAuth
    - `GET /auth/callback/google` – Handle Google OAuth callback (auto-register or login)
    - `GET /auth/logout` – Clear session and log out
  - **`app/routes/main.py`** exposes (all protected by `@login_required` unless noted):
    - `GET /` – Redirects to questions page
    - `GET /questions` – Manage your custom check-in questions (CRUD via stored procedures)
    - `POST /questions/new` – Create a new question
    - `POST /questions/<id>/edit` – Update a question
    - `POST /questions/<id>/delete` – Delete a question
    - `GET /checkins` – View your historical check-ins
    - `GET /checkins/new` – New check-in form
    - `POST /checkins/new` – Create a new check-in session
    - `GET /checkins/<id>` – Answer your custom questions for a check-in
    - `POST /checkins/<id>/edit` – Update check-in notes
    - `POST /checkins/<id>/delete` – Delete check-in and all answers
    - `POST /checkins/<id>/answers/<question_id>` – Save/update answer
    - `POST /checkins/<id>/answers/<question_id>/delete` – Remove answer
    - `GET /summary` – View aggregated daily statistics (mood, scores, trends)
    - `GET /health` – DB connectivity check (returns JSON 200/503, no auth required)
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

pip install --upgrade pip && pip install -r requirements.txt          # installs app plus tooling extras
```

### Configuration

Create a `.env` file in the project root (It will be loaded automatically
by `config.py`):

`SECRET_KEY` is required at import time; the app will fail to start if it is missing.

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password

# Security
SECRET_KEY=your-secure-random-key

# OAuth Configuration (Google)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Environment
FLASK_ENV=development
```

**⚠️ Important**:

- The `SECRET_KEY` environment variable is **required** and must be a secure random string. Generate one with:

  ```bash
  python3 -c 'import secrets; print(secrets.token_hex(32))'
  ```

- For OAuth to work, register your app with Google and add the credentials above.

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Navigate to "APIs & Services" → "Credentials"
4. Click "CREATE CREDENTIALS" → "OAuth client ID"
5. Choose "Web application"
6. Add authorized redirect URI: `http://localhost:5000/auth/callback/google` (development)
7. Copy the Client ID and Client Secret to your `.env` file

The app will fail to start if `SECRET_KEY` is not set in the environment.

### Database Initialization

Use the project helper to apply the schema with the credentials in your
`.env` file:

```bash
invoke execute-schema
```

The command runs `app/database/setup_schema.py`, creating the
`northflow` database plus the `users`, `user_questions`, `checkins`, and
`answers` tables. Note that `schema.sql` drops and recreates the database,
so do not run this against an existing environment. If you prefer to run
the SQL manually, you can still execute
`mysql -u $DB_USER -p < app/database/schema.sql`.

### Stored Routines

`schema.sql` includes stored procedures for user questions, check-ins, answers,
daily summary reporting, plus the `health_check` routine.

### Stored procedure contracts

Use these signatures exactly when calling routines through the DAL:

| Procedure | Required params (in order) |
| --- | --- |
| `health_check` | none |
| `list_user_questions` | none |
| `add_user_question` | `p_user_id`, `p_question_text`, `p_question_type`, `p_is_active`, `p_sort_order` |
| `update_user_question` | `p_question_id`, `p_user_id`, `p_question_text`, `p_question_type`, `p_is_active`, `p_sort_order`, OUT `p_success` |
| `delete_user_question` | `p_question_id`, `p_user_id` |
| `add_checkin` | `p_user_id`, `p_notes` |
| `update_checkin` | `p_checkin_id`, `p_user_id`, `p_notes`, OUT `p_success` |
| `delete_checkin` | `p_checkin_id`, `p_user_id` |
| `get_checkin` | `p_checkin_id`, `p_user_id` |
| `list_checkins` | `p_user_id` |
| `add_answer` | `p_checkin_id`, `p_question_id`, `p_answer_text`, `p_score` |
| `update_answer` | `p_checkin_id`, `p_question_id`, `p_answer_text`, `p_score` |
| `delete_answer` | `p_checkin_id`, `p_question_id` |
| `get_checkin_answers` | `p_checkin_id` |
| `list_daily_summary` | `p_user_id`, `p_start_date`, `p_end_date` (nullable filters; pass `NULL` when unused) |

### Behavioral contracts

- Use stored procedures for app data operations; raw SQL is only allowed in `app/dal/oauth_users.py` (OAuth user lookups).
- All routes require authentication except `/auth/*` and `/health`.
- Include a CSRF token hidden input in every HTML form.
- OAuth callbacks must set `session.permanent = True` (1-hour session lifetime).
- Run `apply_schema_objects` before app start (for example: `MIGRATE_MODE=objects ./deploy/migrate.sh`).

### Data model defaults

- `user_questions.question_type` supported values: `text`, `scale_1_5`, `number`, `boolean`.
- `answers.score` contract is `0` through `5` (enforced by app validation).
- `user_questions.sort_order` defaults to `0`; questions display in ascending `sort_order` (ties by question ID).

### Troubleshooting / runbook

- **App fails at startup with `SECRET_KEY` error**
  - Ensure `.env` includes `SECRET_KEY`, then restart:

    ```bash
    python run.py
    ```

- **`/health` returns 503 due to missing routines/views**
  - Re-apply schema objects, then restart:

    ```bash
    MIGRATE_MODE=objects ./deploy/migrate.sh
    python run.py
    ```

- **Database auth/connection errors**
  - Verify DB env vars in `.env`, then rebuild local schema:

    ```bash
    invoke execute-schema
    python run.py
    ```

- **OAuth login misconfigured (provider/client issues)**
  - Recheck OAuth client IDs/secrets + callback URLs in `.env`, then validate locally:

    ```bash
    python run.py
    pytest tests/
    invoke lint
    ```

## Running the App

```bash
python run.py
```

Visit `http://localhost:5000` to access the application.

### Authentication Flow

1. Navigate to `http://localhost:5000` – you'll be redirected to `/auth/login`
2. Click "Sign in with Google" to authenticate via OAuth 2.0
3. On first login, your account will be auto-created in the database
4. After successful login, you'll be redirected to `/questions`
5. Your user info and logout link will appear in the navigation bar

### Using the Application

Once authenticated:

- **Manage custom prompts** at `/questions` (add/update/delete via stored
  procedures with live refresh). Each user can create personalized check-in questions.
- **Create and manage check-ins** at `/checkins` – create new check-ins and
  record answers to your custom questions. Check-ins capture notes; timestamps
  are set by the database. Question-type aware forms handle text, numeric,
  1-5 scales, and boolean responses.
- **View aggregated daily stats** at `/summary`, with optional date
  filters sourced from the `user_daily_summary` view showing your check-in
  trends over time.

Health endpoint (requires DB connectivity and applied routines):

```bash
curl http://localhost:5000/health
# -> 200 when DB is reachable and health_check exists
# -> 503 when DB is unreachable or health_check is missing
```

`/auth/*` and `/health` are the only endpoints that don't require authentication.

## Deployment

NorthFlow deploys to Railway (web service + MySQL). See
[docs/DEPLOYMENT_ACTIVE.md](docs/DEPLOYMENT_ACTIVE.md) for the deployment model and
migration contract, or [docs/PLAN_DEPLOY_RAILWAY.md](docs/PLAN_DEPLOY_RAILWAY.md) for
the step-by-step setup guide.

For local development, use Docker Compose or run directly with `python run.py`.

### Prerequisites

- Docker (for containerized runs)
- Railway account on the Hobby plan (for cloud deployment)

## Security

NorthFlow implements comprehensive web application security controls:

- **OAuth 2.0 Authentication**: Third-party authentication via Google (no password storage)
- **Session Management**: Persistent sessions with 1-hour timeout, secure cookie settings
- **Protected Routes**: All app endpoints except `/auth/*` and `/health` require authentication via `@login_required`
- **CSRF Protection**: All forms are protected with Flask-WTF CSRF tokens
- **Rate Limiting**: 10 requests/minute on sensitive endpoints (create/update/delete)
- **Input Validation**: Marshmallow schemas validate all user input (length, type, format)
- **Error Handling**: Errors are logged server-side; generic messages shown to users
- **HTTP Security Headers**: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, etc.
- **Secure Sessions**: HTTPOnly, SameSite, and Secure cookie flags enabled
- **Secure Configuration**: `SECRET_KEY` required from environment (no defaults)
- **SQL Parameterization**: All database queries use prepared statements

## Tooling & Quality Gates

- `invoke lint` – run Ruff (Python), SQLFluff (SQL), djlint (HTML/
  Jinja), and pymarkdown (Markdown); auto-fix where supported.
- `invoke lint-python` – Python-only lint/format.
- `invoke lint-sql` – SQL formatting/linting for `app/database` (SQLFluff MySQL dialect).
- `invoke lint-html` – Template lint/format pass via djlint.
- `invoke lint-markdown` – Markdown lint/format pass via pymarkdown.
- `pytest tests/` – runs the DAL test suite (requires a reachable DB
  defined by your `.env`).

## Project Structure

```text
app/
├── __init__.py          # Flask app factory with CSRF, rate limiting, OAuth
├── auth.py              # OAuth configuration and initialization
├── validators.py        # Marshmallow schemas for input validation
├── dal/
│   ├── __init__.py
│   ├── database_connection.py  # DatabaseConnection + DatabaseError
│   ├── user_questions.py       # User questions domain DAL
│   ├── checkins.py             # Check-in domain DAL (CRUD via stored procedures)
│   ├── answers.py              # Answer domain DAL (CRUD via stored procedures)
│   ├── summary.py              # Daily summary domain DAL
│   └── oauth_users.py          # OAuth user management DAL
├── database/
│   ├── schema.sql       # MySQL schema with 10+ stored procedures/views
│   └── setup_schema.py  # Schema application helper
├── routes/
│   ├── __init__.py
│   ├── auth.py          # OAuth authentication routes
│   └── main.py          # Protected application routes
├── services/
│   ├── __init__.py
│   ├── user_questions.py       # Business logic for user questions
│   ├── checkins.py             # Business logic for check-in CRUD
│   ├── answers.py              # Business logic for answer CRUD
│   └── summary.py              # Business logic for daily summary
├── static/
│   ├── css/style.css    # Base styles (OAuth styling)
│   ├── js/main.js       # Placeholder JS hooks
│   └── images/
└── templates/
    ├── base.html        # Layout shell with conditional navigation
    ├── index.html       # Hero + features copy
    ├── login.html       # OAuth login page with Google sign-in button
    ├── questions.html   # user_questions CRUD UI
    ├── checkins.html    # Check-in list and create form
    ├── checkin_detail.html # Check-in detail with dynamic answer forms
    └── summary.html     # Daily aggregation view with filters
config.py                # Environment-aware settings with OAuth config
run.py                   # App entry point
tasks.py                 # Invoke task helpers
tests/test_connection.py # DAL regression tests
```

## License

Released under the MIT License. See `LICENSE` for details.
