# TODO / Next Actions (Definitive)

This file is the source of truth for what must be done next. Remove items as they
are completed.

Items are grouped by priority and carry a stable ID (e.g. `P0-1`) so commits, PRs,
and follow-up notes can reference them. Line numbers were accurate as of the commit
that added each item; re-locate by symbol name if they have drifted.

---

## P0 — Security (do these first)

- [ ] **P0-1: Scope answer writes to the owning user (IDOR).** `save_answer`
  (`app/routes/main.py:354`) and `delete_answer_route` (`app/routes/main.py:383`) pass
  only `checkin_id` and `question_id`; the `add_answer`, `update_answer`, and
  `delete_answer` procedures key solely on those two columns. Any authenticated user can
  create, overwrite, or delete answers on another user's check-in by guessing IDs, and
  can attach a `question_id` belonging to another user. Fix by adding `p_user_id` to the
  three procedures (guard with `EXISTS (SELECT 1 FROM checkins WHERE id = p_checkin_id
  AND user_id = p_user_id)` and the matching `user_questions` ownership check), threading
  `user_id` through `app/dal/answers.py` and `app/services/answers.py`, and passing
  `_get_current_user()` from both routes. Update the stored-procedure contract table in
  `README.md` in the same change.
  **Done when:** a request from user B against user A's `checkin_id` changes no rows and
  flashes a not-found/permission message, and a regression test covers both routes.

- [ ] **P0-2: Scope `get_checkin_answers` to the owning user.** `app/routes/main.py:198`
  fetches answers before checking whether `get_checkin` returned `{}`, and the procedure
  is not user-scoped. Today the template's `{% if checkin %}` wrapper keeps the rows off
  the page, so nothing is currently disclosed — but the unscoped query runs and one
  template edit turns it into a real leak. Add `p_user_id` to `get_checkin_answers` (join
  through `checkins`), and short-circuit the route when `get_checkin` returns empty.
  **Done when:** `/checkins/<id>` for a check-in the session does not own returns a
  redirect or 404 without querying answers.

- [ ] **P0-3: Filter questions in SQL, not in Python.** `list_user_questions()` takes no
  parameters, so `/questions` (`app/routes/main.py:92`) and `/checkins/<id>`
  (`app/routes/main.py:201`) pull every user's question text into the process and filter
  it with a Python comprehension. Add `p_user_id` to the procedure, thread it through
  `app/dal/user_questions.py` and `app/services/user_questions.py`, and drop the
  comprehensions. Update the `README.md` contract table.
  **Done when:** the procedure returns only the requested user's rows and no route
  filters question ownership in Python.

- [ ] **P0-4: Return 404 for a missing or foreign check-in.** `get_checkin`
  (`app/dal/checkins.py:72`) returns `{}`, and `checkin_detail` renders the "New Check-in"
  form for it, so "not yours" and "new" look identical to the user. Redirect to
  `/checkins` with a flash, or abort 404, when the check-in is not found for the session
  user. Pairs naturally with P0-2.
  **Done when:** `/checkins/999999` does not render the new-check-in form.

---

## P1 — Correctness and data quality

- [ ] **P1-1: Boolean answers cannot record "No".** An unchecked checkbox
  (`app/templates/checkin_detail.html:77`) submits nothing, so the save writes `NULL` and
  silently clears a previously saved `"1"` — there is no way to answer "No" or to tell
  "No" from "unanswered". Add a hidden `0` input before the checkbox (or use a
  yes/no radio pair) and accept `"0"`/`"1"` in `AnswerSchema`.
  **Done when:** saving an unchecked boolean question stores `"0"` and the reloaded form
  shows it unchecked rather than blank.

- [ ] **P1-2: `number` answers never reach `score`.** Numeric answers are stored in
  `answer_text`, so they are excluded from `avg_score` / `min_score` / `max_score` in
  `user_daily_summary` — the `/summary` page silently ignores them. Decide and implement
  one of: store numeric answers in `score`, or document the exclusion in `README.md`
  under "Data model defaults". Note the `score` validator caps at 5
  (`app/validators.py:46`), so storing arbitrary numbers there needs a range decision
  first.
  **Done when:** the chosen behavior is implemented and stated in `README.md`.

- [ ] **P1-3: `user_daily_summary` emits rows for users with no check-ins.** The view
  (`app/database/schema.sql:89`) `LEFT JOIN`s from `users`, so a user with zero check-ins
  produces a row with `NULL checkin_date` and zero counts, which renders as a blank-date
  row on `/summary`. Either filter `c.id IS NOT NULL` in the view or skip NULL-date rows
  in `summary.html`.
  **Done when:** a freshly registered user sees an empty-state `/summary`, not a blank row.

- [ ] **P1-4: Remove the unused `list_users` path.** The `list_users` procedure
  (`app/database/schema.sql:121`), `app/dal/user_questions.py:16`, and
  `app/services/user_questions.py:21` are not called by any route — only by
  `tests/test_sql_injection.py:154`. Delete all three (and update the test to target a
  procedure the app actually uses), or document why the procedure is retained.
  **Done when:** no unreferenced data-access path remains, and `invoke lint` passes.

---

## P2 — Testing and CI

- [ ] **P2-2: Add tests that do not require a live MySQL.** Both existing test files
  (`tests/test_connection.py`, `tests/test_sql_injection.py`) need a reachable database,
  so nothing runs in a clean checkout. Add a Flask test-client suite with the DAL mocked,
  covering: `login_required` redirects for every protected route, `validators.py` schema
  behavior, and the service layer's `DatabaseError` wrapping. Use `TestingConfig`
  (CSRF already disabled there).
  **Done when:** `pytest -m "not integration"` passes with no database available.

- [ ] **P2-3: Add ownership regression tests.** Nothing currently proves that a user
  cannot touch another user's data — the P0 bugs would not have been caught. Add tests
  that simulate two sessions and assert cross-user reads and writes fail for check-ins,
  answers, and questions. Mark the DB-dependent ones with the existing `integration`
  marker (`pytest.ini`).
  **Done when:** the P0-1 and P0-2 fixes are covered by failing-before/passing-after tests.

---

## P3 — Deployment and documentation drift

- [ ] **P3-1: Complete the post-deploy verification checklist.** Step 10 of
  `docs/PLAN_DEPLOY_RAILWAY.md:237` is entirely unchecked — there is no record that
  `/health`, both OAuth flows, question/check-in/answer CRUD, and `/summary` were verified
  on the live domain. Run the checks and tick the boxes, noting the date.
  **Done when:** every box in Step 10 is checked or struck with a reason.

- [ ] **P3-2: Document the Cloudflare warmup worker and settle the DNS contradiction.**
  `worker.js` and `wrangler.toml` define a Worker on `northflow.adamlacasse.dev/*` that
  fronts the Railway origin, but neither `README.md` nor `docs/DEPLOYMENT_ACTIVE.md`
  mentions it. Worse, both `docs/DEPLOYMENT_ACTIVE.md:28` and
  `docs/PLAN_DEPLOY_RAILWAY.md:213` say the CNAME should be **DNS only (grey cloud)**,
  while a Worker route requires the hostname to be **proxied (orange cloud)**. Confirm
  which is true in the live zone, then correct the docs and add the worker (deploy
  command, `ORIGIN_URL`/`HEALTH_PATH`/`COLD_TIMEOUT_MS` vars, and its relationship to
  `/health`) to the authoritative deployment doc.
  **Done when:** `docs/DEPLOYMENT_ACTIVE.md` describes the worker and the proxy mode
  matches reality.

- [ ] **P3-3: Fix the stale `update_checkin` row in the README contract table.** The
  table says `update_checkin` takes `OUT p_success`, but the procedure
  (`app/database/schema.sql:256`) takes three `IN` params and returns
  `SELECT (ROW_COUNT() > 0) AS success`; `app/dal/checkins.py:31` matches the procedure.
  Only the documentation is wrong.
  **Done when:** the table matches `schema.sql` for every listed procedure.

- [ ] **P3-4: Refresh `.github/copilot-instructions.md`.** It is the agent-facing guide
  and several sections no longer match the code, which actively misleads future agents.
  Known drift: it describes Google OAuth only (GitHub OAuth also exists); it lists route
  paths that do not exist (`/questions/create`, `/questions/<id>/update`,
  `/checkins/create`, `/checkins/<id>/update`, `/checkins/<id>/answers/<id>/save` — the
  real paths are `/questions/new`, `/questions/<id>/edit`, `/checkins/new`,
  `/checkins/<id>/edit`, `/checkins/<id>/answers/<question_id>`); it says `/health` is the
  only unauthenticated route (`/auth/*` is too); and it claims five tables including an
  `oauth_users` table that does not exist (`schema.sql` defines four: `users`,
  `user_questions`, `checkins`, `answers` — `app/dal/oauth_users.py` is a module, not a
  table). Re-read the code and rewrite those sections.
  **Done when:** every route, table, and provider named in the file exists in the code.

- [ ] **P3-5: Verify the rate-limit storage key is honored.** `config.py:48` sets
  `RATELIMIT_STORAGE_URL`; current Flask-Limiter releases read `RATELIMIT_STORAGE_URI`
  and the old name is deprecated. If it is being ignored, limits fall back to in-memory
  and are enforced per gunicorn worker (three of them, per `deploy/entrypoint.sh`), making
  the documented "10 requests/minute" effectively 30. Check the installed version's
  behavior, rename the key if needed, and decide whether a shared backend is warranted for
  this app's traffic.
  **Done when:** the effective limit is confirmed and `README.md` states it accurately.

- [ ] **P3-6: Fill the gaps in `.env.example`.** It omits `DATABASE` (read by
  `config.py:18`) and the rate-limit variables (`RATELIMIT_STORAGE_URL` / `REDIS_URL`,
  `config.py:48`), so a fresh setup cannot discover them without reading the source.
  **Done when:** every variable `config.py` reads appears in `.env.example`.
