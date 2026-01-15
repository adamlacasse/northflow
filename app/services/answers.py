"""Service layer for answer operations."""

from typing import Any, Dict, List, Optional

from app.dal import DatabaseError
from app.dal.answers import (
    add_answer as dal_add_answer,
)
from app.dal.answers import (
    delete_answer as dal_delete_answer,
)
from app.dal.answers import (
    get_checkin_answers as dal_get_checkin_answers,
)
from app.dal.answers import (
    update_answer as dal_update_answer,
)


def add_answer(
    creds: Dict[str, Any],
    *,
    checkin_id: int,
    question_id: int,
    answer_text: Optional[str] = None,
    score: Optional[float] = None,
) -> None:
    """Add or update an answer to a question in a check-in."""
    try:
        dal_add_answer(
            creds,
            checkin_id=checkin_id,
            question_id=question_id,
            answer_text=answer_text,
            score=score,
        )
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def update_answer(
    creds: Dict[str, Any],
    *,
    checkin_id: int,
    question_id: int,
    answer_text: Optional[str] = None,
    score: Optional[float] = None,
) -> bool:
    """Update an existing answer. Returns True if successful."""
    try:
        return dal_update_answer(
            creds,
            checkin_id=checkin_id,
            question_id=question_id,
            answer_text=answer_text,
            score=score,
        )
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def delete_answer(
    creds: Dict[str, Any],
    *,
    checkin_id: int,
    question_id: int,
) -> None:
    """Delete an answer from a check-in."""
    try:
        dal_delete_answer(
            creds,
            checkin_id=checkin_id,
            question_id=question_id,
        )
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def get_checkin_answers(
    creds: Dict[str, Any],
    *,
    checkin_id: int,
) -> List[Dict[str, Any]]:
    """Get all answers for a specific check-in."""
    try:
        return dal_get_checkin_answers(creds, checkin_id=checkin_id)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
