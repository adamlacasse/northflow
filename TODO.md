# TODO / Next Actions (Definitive)

This file is the source of truth for what must be done next. Remove items as they
are completed.

Items are grouped by priority and carry a stable ID (e.g. `P0-1`) so commits, PRs,
and follow-up notes can reference them. Line numbers were accurate as of the commit
that added each item; re-locate by symbol name if they have drifted.

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
