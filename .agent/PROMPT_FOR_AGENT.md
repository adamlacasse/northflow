You are working inside the NorthFlow repo (Flask + MySQL).

**Before starting work**: Check [TODO.md](../../TODO.md) for the current production roadmap and prioritized items.

Primary goal:
Fix/upgrade `app/database/schema.sql` so it is correct, portable, and rubric-compliant.

Must-do changes:

1) Ensure `user_questions` has `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`
   (because update logic references it).
2) Replace any stored FUNCTION that updates data with a stored PROCEDURE equivalent.
   - Provide `update_user_question` as a PROCEDURE with an OUT parameter `p_success TINYINT(1)`.
   - Validate `question_type` against: ('text','scale_1_5','number','boolean') and SIGNAL on invalid values.

Constraints:

- Keep table names: users, user_questions, checkins, answers
- Keep composite PK on answers: (checkin_id, question_id)
- Keep view `user_daily_summary` and ensure it uses aggregate functions.
- Do not switch seed strategy unless required for correctness:
  - session variables like @user_id and @checkin_id are acceptable
  - do not hardcode numeric ids in INSERT statements

After changes:

- `invoke execute-schema` should work end-to-end
- `pytest tests/` should be able to connect and query using the DAL (given valid .env)
