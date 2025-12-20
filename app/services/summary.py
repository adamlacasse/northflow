from typing import Any, Dict, List, Optional

from app.models import DatabaseConnection


def get_connection(creds: Dict[str, Any]) -> DatabaseConnection:
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
    """Return aggregated daily stats from the user_daily_summary view."""

    query = [
        "SELECT",
        "    user_id,",
        "    CONCAT(first_name, ' ', last_name) AS user_name,",
        "    checkin_date,",
        "    total_checkins,",
        "    total_answers,",
        "    avg_score,",
        "    min_score,",
        "    max_score",
        "FROM user_daily_summary",
        "WHERE 1=1",
    ]
    params: list[Any] = []

    if user_id:
        query.append("  AND user_id = %s")
        params.append(user_id)
    if start_date:
        query.append("  AND checkin_date >= %s")
        params.append(start_date)
    if end_date:
        query.append("  AND checkin_date <= %s")
        params.append(end_date)

    query.append("ORDER BY checkin_date DESC, user_name ASC")

    db = get_connection(creds)
    try:
        return db.execute_query("\n".join(query), tuple(params))
    finally:
        db.close()
