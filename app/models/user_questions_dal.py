from typing import Any, Dict, List

from app.models.dal import DatabaseConnection, DatabaseError


def _get_connection(creds: Dict[str, Any]) -> DatabaseConnection:
    return DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )


def list_users(creds: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = _get_connection(creds)
    try:
        results, _ = db.call_procedure("list_users")
        return results
    finally:
        db.close()


def list_user_questions(creds: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = _get_connection(creds)
    try:
        results, _ = db.call_procedure("list_user_questions")
        return results
    finally:
        db.close()


def create_user_question(
    creds: Dict[str, Any],
    *,
    user_id: int,
    question_text: str,
    question_type: str,
    is_active: bool,
    sort_order: int,
) -> None:
    db = _get_connection(creds)
    try:
        db.call_procedure(
            "add_user_question",
            (
                user_id,
                question_text,
                question_type,
                int(is_active),
                sort_order,
            ),
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
    finally:
        db.close()


def update_user_question(
    creds: Dict[str, Any],
    *,
    question_id: int,
    question_text: str,
    question_type: str,
    is_active: bool,
    sort_order: int,
) -> bool:
    db = _get_connection(creds)
    try:
        _, params = db.call_procedure(
            "update_user_question",
            (
                question_id,
                question_text,
                question_type,
                int(is_active),
                sort_order,
                0,
            ),
        )
        db.commit()
        return bool(params[-1])
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
    finally:
        db.close()


def delete_user_question(creds: Dict[str, Any], *, question_id: int) -> None:
    db = _get_connection(creds)
    try:
        db.call_procedure("delete_user_question", (question_id,))
        db.commit()
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
    finally:
        db.close()
