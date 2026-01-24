# TODO / Open Questions

Use this checklist to align code and docs so future agents can work quickly.

- [ ] Check-in date flow: Decide if check-ins accept a user-supplied `checkin_date` or rely on DB `checkin_time`. Update validators, services, routes, and docs to match the decision.
- [ ] Question params: Confirm required fields for question CRUD (`question_type`, `sort_order`, `is_active`). Ensure forms, routes, services, and stored procedures are consistent and document the contract.
- [ ] OAuth scope: Clarify whether GitHub login is fully supported or experimental; document required env vars for each provider.
- [ ] SECRET_KEY prerequisite: Highlight early in README/setup that app import fails if `SECRET_KEY` is unset; provide generation command.
- [ ] Seed data note: Update schema comment about the demo user now that OAuth is implemented; state current purpose or plan removal.
- [ ] Linting prerequisites: List tooling expectations for `invoke lint` (Ruff, SQLFluff MySQL dialect, djlint, pymarkdown) and any Python/Node version needs.
- [ ] Health endpoint behavior: Document that `/health` returns 503 if the `health_check` routine is missing, to guide readiness checks.
- [ ] Stored procedure contracts: Add a brief table of key procedures and required params (`add_user_question`, `update_user_question`, `add_checkin`, `add_answer`, etc.).
- [ ] Behavioral contracts: Reiterate rules (use stored procedures, no raw SQL except OAuth DAL, all routes authenticated except `/health`, CSRF hidden input, sessions permanent 1h).
- [ ] Troubleshooting/runbook: Common failures (missing SECRET_KEY, missing schema → 503 health, DB auth errors) and quick commands (`invoke execute-schema`, `python run.py`, `pytest tests/`, `invoke lint`).
- [ ] Data model defaults: Document allowed question types, score range (0–5), and how `sort_order` affects display.
