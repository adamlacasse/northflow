from typing import Any, Dict, List, Optional

from app.models.dal import DatabaseConnection


def _get_connection(creds: Dict[str, Any]) -> DatabaseConnection:
    return DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
    )


def list_daily_summary(
    creds: Dict[str, Any],
    *,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return aggregated daily stats via the list_daily_summary stored procedure."""

    db = _get_connection(creds)
    try:
        results, _ = db.call_procedure(
            "list_daily_summary",
            (
                user_id,
                start_date,
                end_date,
            ),
        )
        return results
    finally:
        db.close()
