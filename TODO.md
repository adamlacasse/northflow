# NorthFlow TODOs (course alignment)

## Immediate MVP checklist (due today)

- [x] Run `invoke execute-schema` once to confirm seeds/routines/view `user_daily_summary`
  create cleanly; if time-crunched, at least verify `/health` after app start.
- [x] Ensure login gate collects DB host/port/user/password (db name fixed is fine)
  and blocks access until a connection succeeds; show errors inline.
  - [x] Unsure about the "blocking access" bit. How do I manually test this?
- [x] Expose add/update/delete for `user_questions` via stored procs and refresh the
  list immediately after each mutation.
  - [x] Please explain in more detail how to test this.
- [x] Render the daily summary view (`user_daily_summary`) in a simple table;
  add a basic date/user filter only if time permits.
- [x] Double-check routes/services use the DAL only, and DAL uses stored routines/view
  (no raw SQL in routes).
- [x] Run `invoke lint` (or `lint-python` + `lint-sql`) and `pytest tests/` if DB
  is reachable; otherwise note the gap.
- [x] Update README with current login flow, `.env` requirements, DB init steps,
  and the surfaced advanced feature.

## Short session plan (deadline: tomorrow afternoon)

- Session 1 (≤60 min):
  Validate schema end-to-end with `invoke execute-schema`,
  ensure rubric items hold (≥30 answers, procs/views intact), note gaps.
- Session 2 (≤60 min):
  Implement login gate collecting DB host/port/user/password, enforce layering,
  build CRUD UI for `user_questions` via stored procs with live refresh.
- Session 3 (≤60 min):
  Surface advanced feature in UI (e.g., display/filter/export
  `user_daily_summary`), add targeted tests/docs, run full lint sweep.

## Course alignment checkpoints

- Verify Part 2 rubric stays satisfied: schema.sql runs clean via
  `invoke execute-schema`, answers table maintains >=30 rows, view
  `user_daily_summary` aggregates, add/update/delete procs present.
  **Status:** manual schema checks complete.
- Choose and document the Part 3 advanced feature (see
  `ADVANCED_FEATURE.md` for the current concept, e.g., export
  `user_daily_summary` to CSV, client-side filter, charting) and plan
  supporting routines if needed.

## Database work

- Add/confirm stored procedures to cover the CRUD paths the app will
  expose (user_questions already supported; add check-in/answer procs if
  UI needs them) while keeping DAL usage to stored routines/views.
- Create a lightweight health/read routine if we want to avoid raw
  SELECTs in DAL/health endpoint.
- Re-run `invoke execute-schema` against a fresh MySQL instance to
  validate seeds, constraints, and routines.

## Application/GUI work

- Implement a login screen that collects DB host/port/user/password (db
  name may stay fixed) and gates access before any data loads.
- Separate layers into at least three modules (view, business logic/
  service, DAL); ensure only the DAL talks to the DB via stored
  routines/views.
- Build UI flows to add/update/delete rows in at least one table (use
  existing user_questions procs) and to retrieve/view data; ensure
  updates/deletes cascade visually.
- Wire view refresh so data changes are reflected immediately (e.g.,
  refresh lists after mutations).
- Implement the selected advanced feature and surface it in the UI
  (e.g., export, import, filter, chart, or API mashup).

## Testing & quality

- Extend tests to cover stored procedures and the new app flows (login,
  CRUD, advanced feature) in addition to existing DAL connectivity
  tests.
- Keep linting tasks (`invoke lint`, `invoke lint-python`, `invoke
  lint-sql`, `invoke lint-html`) green after changes.

## Documentation

- Update README as the app evolves so a human can run it locally; keep
  it current-state only (no todos or history), and note any new setup
  for the advanced feature.
