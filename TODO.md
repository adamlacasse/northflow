# TODO / Next Actions (Definitive)

This file is the source of truth for what must be done next. Remove items as they
are completed.

- [ ] Fix template endpoint names in `app/templates/checkins.html` (use `main.new_checkin` for the create form).
- [ ] Fix template endpoint names in `app/templates/checkin_detail.html` (use `main.edit_checkin` for notes updates and `main.save_answer` for answer saves).
- [ ] Fix template endpoint names in `app/templates/questions.html` (use `main.new_question` and `main.edit_question`).
- [ ] Align check-in creation/editing with DB `checkin_time` only: remove the `checkin_date` argument from `app/routes/main.py` calls to `create_checkin` and `update_checkin`; ensure no check-in date field exists in forms or validators.
- [ ] Fix question CRUD parameter flow in `app/routes/main.py`: set `form_data["is_active"] = "is_active" in request.form` before validation, and pass `question_type` and `sort_order` into `create_user_question`/`update_user_question`.
- [ ] Update the seed user note in `app/database/schema.sql` to reflect OAuth reality (demo user is optional for local dev and should not be used in production).
- [ ] Add a "Stored procedure contracts" table to `README.md` listing procedure names and required params for `health_check`, `list_user_questions`, `add_user_question`, `update_user_question`, `delete_user_question`, `add_checkin`, `update_checkin`, `delete_checkin`, `get_checkin`, `list_checkins`, `add_answer`, `update_answer`, `delete_answer`, `get_checkin_answers`, `list_daily_summary`.
- [ ] Add a "Behavioral contracts" section to `README.md` with the explicit rules: stored procedures only (raw SQL only in `app/dal/oauth_users.py`), all routes auth except `/auth/*` and `/health`, CSRF token in all forms, sessions permanent 1h, run `apply_schema_objects` before app start.
- [ ] Add a "Troubleshooting / runbook" section to `README.md` covering missing `SECRET_KEY`, missing schema routines (`/health` 503), DB auth errors, and OAuth misconfig, with the exact commands to fix (`invoke execute-schema`, `MIGRATE_MODE=objects ./deploy/migrate.sh`, `python run.py`, `pytest tests/`, `invoke lint`).
- [ ] Add a "Data model defaults" section to `README.md` documenting allowed question types (`text`, `scale_1_5`, `number`, `boolean`), score range (0-5), and `sort_order` display behavior.
- [ ] After any README/TODO changes, sync `infra/text/asset.9ace2a67483fdbe49d08c0de2e18c743664aceb8bca1aa29fc42590b955a30da/README.md` and `infra/text/asset.9ace2a67483fdbe49d08c0de2e18c743664aceb8bca1aa29fc42590b955a30da/TODO.md` to match.
