from typing import Any, Dict, List

from app.models import DatabaseConnection, DatabaseError


def get_connection(creds: Dict[str, Any]) -> DatabaseConnection:
    return DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )


def list_users(creds: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = get_connection(creds)
    try:
        return db.execute_query(
            """
                SELECT id,
                    first_name,
                    last_name,
                    email
                FROM users
                ORDER BY last_name, first_name
            """
        )
    finally:
        db.close()


def list_user_questions(creds: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = get_connection(creds)
    try:
        return db.execute_query(
            """
            SELECT
                uq.id,
                uq.user_id,
                CONCAT(u.first_name, ' ', u.last_name) AS user_name,
                uq.question_text,
                uq.question_type,
                uq.is_active,
                uq.sort_order
            FROM user_questions AS uq
            JOIN users AS u ON u.id = uq.user_id
            ORDER BY u.last_name, u.first_name, uq.sort_order, uq.id
            """
        )
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
    db = get_connection(creds)
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
    db = get_connection(creds)
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
    db = get_connection(creds)
    try:
        db.call_procedure("delete_user_question", (question_id,))
        db.commit()
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
    finally:
        db.close()
