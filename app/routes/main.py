"""Main routes blueprint."""

from flask import Blueprint, render_template
from app.models import DatabaseConnection, DatabaseError

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Homepage."""
    return render_template("index.html")


@bp.route("/health")
def health():
    """Health check endpoint."""
    try:
        db = DatabaseConnection()
        db.execute_query("SELECT 1 as status")
        db.close()
        return {"status": "healthy", "database": "connected"}, 200
    except DatabaseError as e:
        return {"status": "unhealthy", "error": str(e)}, 503
