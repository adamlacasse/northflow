"""Unit tests for app/validators.py marshmallow schemas.

Pure Python, no database or Flask app context required.
"""

from app.validators import (
    AnswerSchema,
    CheckinSchema,
    QuestionSchema,
    SummaryFilterSchema,
    validate_form,
)


class TestAnswerSchema:
    def test_boolean_checked_value_accepted(self):
        """P1-1: a checked boolean answer submits answer_text='1'."""
        is_valid, cleaned, error = validate_form(AnswerSchema, {"answer_text": "1"})
        assert is_valid, error
        assert cleaned["answer_text"] == "1"

    def test_boolean_unchecked_hidden_fallback_accepted(self):
        """P1-1: an unchecked boolean answer submits the hidden answer_text='0'."""
        is_valid, cleaned, error = validate_form(AnswerSchema, {"answer_text": "0"})
        assert is_valid, error
        assert cleaned["answer_text"] == "0"

    def test_answer_text_optional(self):
        is_valid, cleaned, error = validate_form(AnswerSchema, {})
        assert is_valid, error
        assert cleaned.get("answer_text") is None

    def test_answer_text_too_long_rejected(self):
        is_valid, cleaned, error = validate_form(
            AnswerSchema, {"answer_text": "x" * 2001}
        )
        assert not is_valid
        assert "2000" in error

    def test_score_in_range_accepted(self):
        is_valid, cleaned, error = validate_form(AnswerSchema, {"score": 3})
        assert is_valid, error
        assert cleaned["score"] == 3.0

    def test_score_below_zero_rejected(self):
        is_valid, cleaned, error = validate_form(AnswerSchema, {"score": -1})
        assert not is_valid

    def test_score_above_five_rejected(self):
        is_valid, cleaned, error = validate_form(AnswerSchema, {"score": 5.5})
        assert not is_valid

    def test_unknown_fields_are_ignored(self):
        """csrf_token and other stray form fields should not fail validation."""
        is_valid, cleaned, error = validate_form(
            AnswerSchema, {"answer_text": "hi", "csrf_token": "abc"}
        )
        assert is_valid, error
        assert "csrf_token" not in cleaned


class TestQuestionSchema:
    def test_valid_question(self):
        is_valid, cleaned, error = validate_form(
            QuestionSchema,
            {
                "question_text": "How did you sleep?",
                "question_type": "scale_1_5",
                "is_active": True,
                "sort_order": 1,
            },
        )
        assert is_valid, error
        assert cleaned["question_type"] == "scale_1_5"

    def test_invalid_question_type_rejected(self):
        is_valid, cleaned, error = validate_form(
            QuestionSchema,
            {"question_text": "x", "question_type": "not_a_type"},
        )
        assert not is_valid

    def test_missing_question_text_rejected(self):
        is_valid, cleaned, error = validate_form(
            QuestionSchema, {"question_type": "text"}
        )
        assert not is_valid

    def test_defaults_applied(self):
        is_valid, cleaned, error = validate_form(
            QuestionSchema, {"question_text": "x", "question_type": "text"}
        )
        assert is_valid, error
        assert cleaned["is_active"] is True
        assert cleaned["sort_order"] == 0


class TestCheckinSchema:
    def test_notes_optional(self):
        is_valid, cleaned, error = validate_form(CheckinSchema, {})
        assert is_valid, error

    def test_notes_too_long_rejected(self):
        is_valid, cleaned, error = validate_form(
            CheckinSchema, {"notes": "x" * 2001}
        )
        assert not is_valid


class TestSummaryFilterSchema:
    def test_valid_dates(self):
        is_valid, cleaned, error = validate_form(
            SummaryFilterSchema,
            {"start_date": "2024-01-01", "end_date": "2024-01-31"},
        )
        assert is_valid, error

    def test_invalid_date_rejected(self):
        is_valid, cleaned, error = validate_form(
            SummaryFilterSchema, {"start_date": "not-a-date"}
        )
        assert not is_valid
