"""Unit tests for the service layer's DatabaseError wrapping.

The DAL is mocked out entirely, so no database connection is made.
"""

from unittest.mock import patch

import pytest

from app.dal import DatabaseError
from app.services import answers as answers_service
from app.services import checkins as checkins_service
from app.services import user_questions as user_questions_service

CREDS = {"host": "x", "user": "x", "password": "x", "database": "x", "port": 3306}


class TestAnswersServiceWrapping:
    def test_add_answer_wraps_exception(self):
        with patch.object(
            answers_service, "dal_add_answer", side_effect=RuntimeError("boom")
        ):
            with pytest.raises(DatabaseError):
                answers_service.add_answer(
                    CREDS, checkin_id=1, question_id=1, user_id=1
                )

    def test_add_answer_returns_dal_result(self):
        with patch.object(answers_service, "dal_add_answer", return_value=True):
            assert (
                answers_service.add_answer(
                    CREDS, checkin_id=1, question_id=1, user_id=1
                )
                is True
            )

    def test_delete_answer_wraps_exception(self):
        with patch.object(
            answers_service, "dal_delete_answer", side_effect=RuntimeError("boom")
        ):
            with pytest.raises(DatabaseError):
                answers_service.delete_answer(
                    CREDS, checkin_id=1, question_id=1, user_id=1
                )

    def test_get_checkin_answers_wraps_exception(self):
        with patch.object(
            answers_service,
            "dal_get_checkin_answers",
            side_effect=RuntimeError("boom"),
        ):
            with pytest.raises(DatabaseError):
                answers_service.get_checkin_answers(CREDS, checkin_id=1, user_id=1)


class TestCheckinsServiceWrapping:
    def test_create_checkin_wraps_exception(self):
        with patch.object(
            checkins_service, "dal_create_checkin", side_effect=RuntimeError("boom")
        ):
            with pytest.raises(DatabaseError):
                checkins_service.create_checkin(CREDS, user_id=1, notes="hi")

    def test_get_checkin_wraps_exception(self):
        with patch.object(
            checkins_service, "dal_get_checkin", side_effect=RuntimeError("boom")
        ):
            with pytest.raises(DatabaseError):
                checkins_service.get_checkin(CREDS, checkin_id=1, user_id=1)


class TestUserQuestionsServiceWrapping:
    def test_create_user_question_wraps_exception(self):
        with patch.object(
            user_questions_service,
            "dal_create_user_question",
            side_effect=RuntimeError("boom"),
        ):
            with pytest.raises(DatabaseError):
                user_questions_service.create_user_question(
                    CREDS,
                    user_id=1,
                    question_text="x",
                    question_type="text",
                    is_active=True,
                    sort_order=0,
                )

    def test_delete_user_question_wraps_exception(self):
        with patch.object(
            user_questions_service,
            "dal_delete_user_question",
            side_effect=RuntimeError("boom"),
        ):
            with pytest.raises(DatabaseError):
                user_questions_service.delete_user_question(
                    CREDS, question_id=1, user_id=1
                )

    def test_list_user_questions_passes_user_id(self):
        with patch.object(
            user_questions_service, "dal_list_user_questions", return_value=[]
        ) as mocked:
            user_questions_service.list_user_questions(CREDS, user_id=42)
            mocked.assert_called_once_with(CREDS, user_id=42)
