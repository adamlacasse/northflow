from typing import Any, Dict, List, Optional

from app.models.summary_dal import list_daily_summary as dal_list_daily_summary


def list_daily_summary(
    creds: Dict[str, Any],
    *,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return aggregated daily stats via a stored procedure wrapper."""

    return dal_list_daily_summary(
        creds,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
