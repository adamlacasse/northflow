"""Data access layer for check-in operations."""

from typing import Any, Dict, List

from app.dal.database_connection import DatabaseConnection, DatabaseError


def create_checkin(
    creds: Dict[str, Any],
    user_id: int,
    notes: str = "",
) -> int:
    """Create a new check-in and return its ID."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        results, _ = db.call_procedure("add_checkin", (user_id, notes))
        db.commit()
        if results:
            return results[0]["checkin_id"]
        raise DatabaseError("Failed to create check-in (no ID returned)")
    finally:
        db.close()


def update_checkin(
    creds: Dict[str, Any],
    checkin_id: int,
    user_id: int,
    notes: str = "",
) -> bool:
    """Update a check-in's notes. Returns True if a row owned by user_id was updated."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        _, updated_params = db.call_procedure(
            "update_checkin", (checkin_id, user_id, notes, 0)
        )
        db.commit()
        # The OUT parameter p_success is in updated_params
        return updated_params[3] == 1
    finally:
        db.close()


def delete_checkin(creds: Dict[str, Any], checkin_id: int, user_id: int) -> None:
    """Delete a check-in owned by user_id and all associated answers."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        db.call_procedure("delete_checkin", (checkin_id, user_id))
        db.commit()
    finally:
        db.close()


def get_checkin(creds: Dict[str, Any], checkin_id: int, user_id: int) -> Dict[str, Any]:
    """Retrieve a single check-in by ID, scoped to the owning user."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        results, _ = db.call_procedure("get_checkin", (checkin_id, user_id))
        if results:
            return results[0]
        return {}
    finally:
        db.close()


def list_checkins(
    creds: Dict[str, Any],
    user_id: int,
) -> List[Dict[str, Any]]:
    """List all check-ins for a specific user."""
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )
    try:
        results, _ = db.call_procedure("list_checkins", (user_id,))
        return results
    finally:
        db.close()
