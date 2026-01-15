# NorthFlow — Agent Context (for Codex/Copilot)

## What this repo is

NorthFlow is a Flask-based mindfulness/gratitude check-in app created for CSC-6302 Database Principles.
The live UI is intentionally minimal; the focus is the MySQL schema + Python DAL + deployment/quality gates.

## Course project deliverables (per assignment)

- Part 1 (planning): ER diagram plus written responses; no AI assistance for diagram/answers.
- Part 2 (database): single SQL file; ≥4 tables with data; ≥2 FKs; ≥1 composite PK (not a lone int id); 3NF; datatype coverage (datetime, numeric/decimal, enum, boolean/tinyint); largest table ≥30 rows; aggregated view/procedure; add/update/delete procedures with cascading changes; data should be viewer-friendly; use stored routines/views to support advanced feature.
- Part 3 (GUI app): zip submission; README with run steps and advanced feature; ≥3 modules separating view/business logic/DAL; only DAL hits DB via stored routines/views; connection info entered at login (host/port editable, db name ok to fix); GUI must show status/errors; login gate before data; ability to add/update/delete rows and view data with live reflection; advanced feature (e.g., export/import/filter/charts/API); app must not crash.

Advanced feature concept is tracked in [ADVANCED_FEATURE.md](ADVANCED_FEATURE.md).

Action items are tracked in project docs and issues (no `TODO.md` is required by this repo).

## Where important stuff lives

- MySQL schema bootstrap: `app/database/schema.sql` (10 stored procedures + 1 view)
- Schema runner: `app/database/setup_schema.py` (invoked by `invoke execute-schema`)
- DAL wrapper: `app/dal/database_connection.py` (uses mysql-connector-python, standardized DatabaseError)
- DAL modules:
  - `app/dal/user_questions.py` — User questions CRUD via stored procedures
  - `app/dal/checkins.py` — Check-in CRUD via stored procedures
  - `app/dal/answers.py` — Answer CRUD via stored procedures
  - `app/dal/summary.py` — Daily summary view wrapper
- Service modules (business logic with error handling):
  - `app/services/user_questions.py`
  - `app/services/checkins.py`
  - `app/services/answers.py`
  - `app/services/summary.py`
- Routes: `app/routes/main.py` (14 endpoints covering auth, questions, check-ins, answers, summary, health)
- Templates: `app/templates/` (6 HTML files with clean separation of concerns)
- Tests: `tests/test_connection.py` (expects DB credentials from `.env`)

## Assignment/rubric constraints (schema.sql must satisfy) ✅ MET

- ✅ ≥ 4 tables with data loaded (users, user_questions, checkins, answers)
- ✅ ≥ 2 tables include foreign keys (all 4 have them)
- ✅ ≥ 1 table has a composite primary key (answers: checkin_id, question_id)
- ✅ Tables in 3NF
- ✅ All datatype groups used:
  - Date/Time: TIMESTAMP on users, checkins, user_questions, answers
  - Numeric/Decimal: DECIMAL(5,2) on answers.score
  - Enum: ENUM on user_questions.question_type
  - Boolean/TinyInt: TINYINT(1) on user_questions.is_active
- ✅ Largest table ≥ 30 rows (answers has 40+ rows of seed data)
- ✅ View + stored procedures with aggregates (user_daily_summary view + 10 procedures)
- ✅ Data is viewer-friendly (named users, meaningful questions/answers)

## Part 3 Implementation Status (GUI app)

- ✅ ≥3 modules separating view/business logic/DAL (5 DAL modules + 4 service modules + routes)
- ✅ Only DAL hits DB via stored procedures/views (never raw SQL in routes)
- ✅ Connection info entered at login (host/port/user/password editable)
- ✅ GUI shows status/errors (flash messages with color-coded alerts)
- ✅ Login gate before data (all protected routes check session credentials)
- ✅ Full CRUD on rows (user_questions and check-ins fully functional)
- ✅ Live reflection (summary view shows aggregated data based on check-ins)
- ✅ Advanced feature implemented (user_daily_summary view with filtering)
- ✅ App stability (proper error handling, no unhandled exceptions)

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

## Stored Procedures (schema.sql)

**User Questions CRUD:**
- `add_user_question()` — Create custom question for user
- `update_user_question()` — Update question (returns success flag)
- `delete_user_question()` — Delete question (cascades answers)
- `list_user_questions()` — List all questions with user names
- `list_users()` — List all users (supports check-in/question filtering)

**Check-in CRUD:**
- `add_checkin()` — Create check-in (returns new ID)
- `update_checkin()` — Update check-in notes (returns success flag)
- `delete_checkin()` — Delete check-in (cascades answers)
- `get_checkin()` — Retrieve single check-in with user details
- `list_checkins()` — List check-ins for a user with answer counts

**Answer CRUD:**
- `add_answer()` — Add/upsert answer (supports text, numeric, scored responses)
- `update_answer()` — Update answer (returns success flag)
- `delete_answer()` — Remove answer
- `get_checkin_answers()` — Get all answers for a check-in with question metadata

**Utilities:**
- `health_check()` — Simple connectivity test
- `list_daily_summary()` — Wrapper for user_daily_summary view with filters

All use `ON DELETE CASCADE` for referential integrity. Procedures return dictionaries via dictionary cursors for consistent JSON-like results.
