# NorthFlow — Agent Context (for Codex/Copilot)

## What this repo is

NorthFlow is a Flask-based mindfulness/gratitude check-in app created for CSC-6302 Database Principles.
The live UI is intentionally minimal; the focus is the MySQL schema + Python DAL + deployment/quality gates.

## Course project deliverables (per assignment)

- Part 1 (planning): ER diagram plus written responses; no AI assistance for diagram/answers.
- Part 2 (database): single SQL file; ≥4 tables with data; ≥2 FKs; ≥1 composite PK (not a lone int id); 3NF; datatype coverage (datetime, numeric/decimal, enum, boolean/tinyint); largest table ≥30 rows; aggregated view/procedure; add/update/delete procedures with cascading changes; data should be viewer-friendly; use stored routines/views to support advanced feature.
- Part 3 (GUI app): zip submission; README with run steps and advanced feature; ≥3 modules separating view/business logic/DAL; only DAL hits DB via stored routines/views; connection info entered at login (host/port editable, db name ok to fix); GUI must show status/errors; login gate before data; ability to add/update/delete rows and view data with live reflection; advanced feature (e.g., export/import/filter/charts/API); app must not crash.

Advanced feature concept is tracked in [ADVANCED_FEATURE.md](ADVANCED_FEATURE.md).

See TODOs tracked in `TODO.md` (project root) for current action items aligned to these deliverables.

## Where important stuff lives

- MySQL schema bootstrap: `app/database/schema.sql`
- Schema runner: `app/database/setup_schema.py` (invoked by `invoke execute-schema`)
- DAL wrapper: `app/models/dal.py` (uses mysql-connector-python, standardized DatabaseError)
- Routes: `app/routes/main.py` (GET /, GET /health)
- Tests: `tests/test_connection.py` (expects DB credentials from `.env`)

## Assignment/rubric constraints (schema.sql must satisfy)

- ≥ 4 tables with data loaded
- ≥ 2 tables include foreign keys
- ≥ 1 table has a composite primary key (not a standalone int id)
- Tables in 3NF
- Must use at least one of each datatype group:
  - Date/Time/Datetime (TIMESTAMP/DATETIME ok)
  - Numeric/Decimal (DECIMAL ok)
  - Enum (ENUM ok)
  - Boolean/TinyInt (TINYINT(1) ok)
- Largest table ≥ 30 rows of seed data
- At least one view or stored procedure that reads/aggregates (must include an aggregate function)
- Data should be viewer-friendly

## Current DB design (northflow)

Tables:

1) `users`
2) `user_questions` (custom prompts per user)
3) `checkins` (a check-in event per user)
4) `answers` (answers per (checkin, question) pair)

Keys:

- `answers` uses composite PK: (checkin_id, question_id)

Foreign keys (ON DELETE CASCADE):

- user_questions.user_id -> users.id
- checkins.user_id -> users.id
- answers.checkin_id -> checkins.id
- answers.question_id -> user_questions.id

Aggregation requirement:

- View `user_daily_summary` groups by user + DATE(checkin_time)
- Uses COUNT/AVG/MIN/MAX aggregates

Seed strategy:

- No hardcoded numeric ids in INSERTs.
- It is acceptable to SELECT ids into session variables (e.g., @avery_id, @checkin1) and reuse them.
- Ensure `answers` ends with ≥ 30 rows.

Routines:

- Stored procedures should be preferred over stored functions for updates (portability and fewer MySQL restrictions).
