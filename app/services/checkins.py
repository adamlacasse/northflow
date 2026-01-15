"""Service layer for check-in operations."""

from typing import Any, Dict, List

from app.dal import DatabaseError
from app.dal.checkins import (
    create_checkin as dal_create_checkin,
)
from app.dal.checkins import (
    delete_checkin as dal_delete_checkin,
)
from app.dal.checkins import (
    get_checkin as dal_get_checkin,
)
from app.dal.checkins import (
    list_checkins as dal_list_checkins,
)
from app.dal.checkins import (
    update_checkin as dal_update_checkin,
)


def create_checkin(
    creds: Dict[str, Any],
    *,
    user_id: int,
    notes: str = "",
) -> int:
    """Create a new check-in and return its ID."""
    try:
        return dal_create_checkin(creds, user_id=user_id, notes=notes)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def update_checkin(
    creds: Dict[str, Any],
    *,
    checkin_id: int,
    notes: str = "",
) -> bool:
    """Update a check-in's notes. Returns True if successful."""
    try:
        return dal_update_checkin(creds, checkin_id=checkin_id, notes=notes)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def delete_checkin(creds: Dict[str, Any], *, checkin_id: int) -> None:
    """Delete a check-in and all associated answers."""
    try:
        dal_delete_checkin(creds, checkin_id=checkin_id)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def get_checkin(creds: Dict[str, Any], *, checkin_id: int) -> Dict[str, Any]:
    """Retrieve a single check-in by ID."""
    try:
        return dal_get_checkin(creds, checkin_id=checkin_id)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc


def list_checkins(creds: Dict[str, Any], *, user_id: int) -> List[Dict[str, Any]]:
    """List all check-ins for a specific user."""
    try:
        return dal_list_checkins(creds, user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        raise DatabaseError(str(exc)) from exc
