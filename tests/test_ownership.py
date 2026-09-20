"""Ownership regression tests for the P0-1/P0-2 IDOR fixes.

These tests simulate two different logged-in users against the same
check-in/question/answer IDs, with the DAL mocked to behave the way the
fixed stored procedures behave: a write or read against a resource owned
by a different user changes/returns nothing. They run without a database.

True end-to-end coverage against a live MySQL instance (exercising the
actual stored procedures) is marked `integration` and skipped by
`pytest -m "not integration"`.
"""

from unittest.mock import patch

import pytest

from tests.conftest import login_as

# user 1 owns checkin_id=1 and question_id=1. user 2 is a different,
# unrelated user who should never be able to touch user 1's data.
OWNER_USER_ID = 1
OTHER_USER_ID = 2
CHECKIN_ID = 1
QUESTION_ID = 1


def test_save_answer_denied_for_non_owner(client):
    """P0-1: user 2 saving an answer against user 1's checkin_id is a no-op."""
    login_as(client, OTHER_USER_ID)

    with patch("app.routes.main.add_answer") as mocked_add_answer:
        # The stored procedure guard returns False (no rows changed) when
        # the checkin/question isn't owned by the requesting user.
        mocked_add_answer.return_value = False

        response = client.post(
            f"/checkins/{CHECKIN_ID}/answers/{QUESTION_ID}",
            data={"answer_text": "hacked"},
            follow_redirects=True,
        )

        # The route must pass the *requesting* user's id, not trust the URL.
        _, kwargs = mocked_add_answer.call_args
        assert kwargs["user_id"] == OTHER_USER_ID
        assert kwargs["checkin_id"] == CHECKIN_ID
        assert kwargs["question_id"] == QUESTION_ID

    assert response.status_code == 200
    assert b"don&#39;t have permission" in response.data or (
        b"permission" in response.data
    )


def test_save_answer_allowed_for_owner(client):
    """Sanity check: the same call succeeds for the resource's actual owner."""
    login_as(client, OWNER_USER_ID)

    with patch("app.routes.main.add_answer") as mocked_add_answer:
        mocked_add_answer.return_value = True

        response = client.post(
            f"/checkins/{CHECKIN_ID}/answers/{QUESTION_ID}",
            data={"answer_text": "hello"},
            follow_redirects=True,
        )

        _, kwargs = mocked_add_answer.call_args
        assert kwargs["user_id"] == OWNER_USER_ID

    assert response.status_code == 200
    assert b"Answer saved" in response.data


def test_delete_answer_denied_for_non_owner(client):
    """P0-1: user 2 deleting user 1's answer is a no-op."""
    login_as(client, OTHER_USER_ID)

    with patch("app.routes.main.delete_answer") as mocked_delete_answer:
        mocked_delete_answer.return_value = False

        response = client.post(
            f"/checkins/{CHECKIN_ID}/answers/{QUESTION_ID}/delete",
            follow_redirects=True,
        )

        _, kwargs = mocked_delete_answer.call_args
        assert kwargs["user_id"] == OTHER_USER_ID

    assert response.status_code == 200
    assert b"permission" in response.data


def test_delete_answer_allowed_for_owner(client):
    login_as(client, OWNER_USER_ID)

    with patch("app.routes.main.delete_answer") as mocked_delete_answer:
        mocked_delete_answer.return_value = True

        response = client.post(
            f"/checkins/{CHECKIN_ID}/answers/{QUESTION_ID}/delete",
            follow_redirects=True,
        )

        _, kwargs = mocked_delete_answer.call_args
        assert kwargs["user_id"] == OWNER_USER_ID

    assert response.status_code == 200
    assert b"Answer deleted" in response.data


def test_checkin_detail_not_found_or_foreign_redirects(client):
    """P0-2/P0-4: a missing or foreign check-in redirects instead of
    rendering a blank 'New Check-in' form."""
    login_as(client, OTHER_USER_ID)

    with patch("app.routes.main.get_checkin", return_value={}) as mocked_get_checkin:
        response = client.get(f"/checkins/{CHECKIN_ID}", follow_redirects=False)

        _, kwargs = mocked_get_checkin.call_args
        assert kwargs["user_id"] == OTHER_USER_ID

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/checkins")


def test_checkin_detail_scopes_answers_to_requesting_user(client):
    """P0-2: get_checkin_answers must be called with the requesting user's id."""
    login_as(client, OWNER_USER_ID)

    fake_checkin = {
        "id": CHECKIN_ID,
        "user_id": OWNER_USER_ID,
        "notes": "",
        "checkin_time": "now",
    }
    with patch("app.routes.main.get_checkin", return_value=fake_checkin), patch(
        "app.routes.main.get_checkin_answers", return_value=[]
    ) as mocked_answers, patch(
        "app.routes.main.list_user_questions", return_value=[]
    ) as mocked_questions:
        response = client.get(f"/checkins/{CHECKIN_ID}")

        _, kwargs = mocked_answers.call_args
        assert kwargs["user_id"] == OWNER_USER_ID
        assert kwargs["checkin_id"] == CHECKIN_ID

        _, q_kwargs = mocked_questions.call_args
        assert q_kwargs["user_id"] == OWNER_USER_ID

    assert response.status_code == 200


def test_questions_scoped_to_requesting_user(client):
    """P0-3: /questions must ask the DAL for only the requesting user's
    questions, not filter a full list in Python."""
    login_as(client, OWNER_USER_ID)

    with patch(
        "app.routes.main.list_user_questions", return_value=[]
    ) as mocked_questions:
        response = client.get("/questions")

        _, kwargs = mocked_questions.call_args
        assert kwargs["user_id"] == OWNER_USER_ID

    assert response.status_code == 200


@pytest.mark.integration
def test_cross_user_answer_write_denied_live_db():
    """End-to-end version of test_save_answer_denied_for_non_owner against a
    real MySQL instance and the actual stored procedures.

    Requires DB_HOST/DB_USER/DB_PASSWORD/DATABASE env vars pointing at a
    database with the schema applied, and at least two distinct users with
    an existing check-in/question owned by the first user only.
    """
    import os

    from app.services.answers import add_answer
    from app.services.checkins import create_checkin
    from app.services.user_questions import create_user_question

    creds = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DATABASE", "northflow"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }

    # Assumes user id 1 exists (seeded demo user) and a second user exists
    # or can be created out of band; kept minimal/skippable if not.
    owner_id = 1
    other_id = 2

    checkin_id = create_checkin(creds, user_id=owner_id, notes="integration test")
    create_user_question(
        creds,
        user_id=owner_id,
        question_text="integration test question",
        question_type="text",
        is_active=True,
        sort_order=0,
    )

    # Fetch the question id we just made.
    from app.services.user_questions import list_user_questions

    questions = list_user_questions(creds, user_id=owner_id)
    question_id = questions[-1]["id"]

    # A different user must not be able to write an answer against owner_id's
    # checkin/question.
    saved = add_answer(
        creds,
        checkin_id=checkin_id,
        question_id=question_id,
        user_id=other_id,
        answer_text="should not be saved",
    )
    assert saved is False
