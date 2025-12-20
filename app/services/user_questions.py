from typing import Any, Dict, List

from app.dal import DatabaseError
from app.dal.user_questions_dal import (
    create_user_question as dal_create_user_question,
)
from app.dal.user_questions_dal import (
    delete_user_question as dal_delete_user_question,
)
from app.dal.user_questions_dal import (
    list_user_questions as dal_list_user_questions,
)
from app.dal.user_questions_dal import (
    list_users as dal_list_users,
)
from app.dal.user_questions_dal import (
    update_user_question as dal_update_user_question,
)


def list_users(creds: Dict[str, Any]) -> List[Dict[str, Any]]:
    return dal_list_users(creds)


def list_user_questions(creds: Dict[str, Any]) -> List[Dict[str, Any]]:
    return dal_list_user_questions(creds)


def create_user_question(
    creds: Dict[str, Any],
    *,
    user_id: int,
    question_text: str,
    question_type: str,
    is_active: bool,
    sort_order: int,
) -> None:
    try:
        dal_create_user_question(
            creds,
            user_id=user_id,
            question_text=question_text,
            question_type=question_type,
            is_active=is_active,
            sort_order=sort_order,
        )
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def update_user_question(
    creds: Dict[str, Any],
    *,
    question_id: int,
    question_text: str,
    question_type: str,
    is_active: bool,
    sort_order: int,
) -> bool:
    try:
        return dal_update_user_question(
            creds,
            question_id=question_id,
            question_text=question_text,
            question_type=question_type,
            is_active=is_active,
            sort_order=sort_order,
        )
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def delete_user_question(creds: Dict[str, Any], *, question_id: int) -> None:
    try:
        dal_delete_user_question(creds, question_id=question_id)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
