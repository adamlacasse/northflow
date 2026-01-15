"""Data access layer for answer operations."""

from typing import Any, Dict, List, Optional

from app.dal.database_connection import DatabaseConnection


def add_answer(
    creds: Dict[str, Any],
    checkin_id: int,
    question_id: int,
    answer_text: Optional[str] = None,
    score: Optional[float] = None,
) -> None:
    """Add or update an answer to a question in a check-in."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        db.call_procedure(
            "add_answer",
            (checkin_id, question_id, answer_text, score),
        )
        db.commit()
    finally:
        db.close()


def update_answer(
    creds: Dict[str, Any],
    checkin_id: int,
    question_id: int,
    answer_text: Optional[str] = None,
    score: Optional[float] = None,
) -> bool:
    """Update an existing answer. Returns True if successful."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        _, updated_params = db.call_procedure(
            "update_answer",
            (checkin_id, question_id, answer_text, score, 0),
        )
        # The OUT parameter p_success is in updated_params
        return updated_params[4] == 1
    finally:
        db.close()


def delete_answer(
    creds: Dict[str, Any],
    checkin_id: int,
    question_id: int,
) -> None:
    """Delete an answer from a check-in."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        db.call_procedure("delete_answer", (checkin_id, question_id))
        db.commit()
    finally:
        db.close()


def get_checkin_answers(
    creds: Dict[str, Any],
    checkin_id: int,
) -> List[Dict[str, Any]]:
    """Get all answers for a specific check-in."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        results, _ = db.call_procedure("get_checkin_answers", (checkin_id,))
        return results
    finally:
        db.close()
