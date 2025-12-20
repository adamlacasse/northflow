"""Main routes blueprint."""

from typing import Any, Dict

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models import DatabaseConnection, DatabaseError
from app.services.summary import list_daily_summary
from app.services.user_questions import (
    create_user_question,
    delete_user_question,
    list_user_questions,
    list_users,
    update_user_question,
)
from config import Config

bp = Blueprint("main", __name__)


def _db_creds() -> Dict[str, Any]:
    return session.get(
        "db_credentials",
        {
            "host": Config.DB_HOST,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DATABASE,
            "port": 3306,
        },
    )


def _require_login():
    if "db_credentials" not in session:
        flash("Please connect to the database to continue.", "warning")
        return False
    return True


@bp.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        host = request.form.get("db_host", "").strip() or Config.DB_HOST
        user = request.form.get("db_user", "").strip() or Config.DB_USER
        password = request.form.get("db_password", "")
        port_raw = request.form.get("db_port", "").strip()
        port = int(port_raw) if port_raw else 3306

        try:
            db = DatabaseConnection(
                host=host,
                user=user,
                password=password,
                database=Config.DATABASE,
                port=port,
            )
            db.close()
            session["db_credentials"] = {
                "host": host,
                "user": user,
                "password": password,
                "database": Config.DATABASE,
                "port": port,
            }
            flash("Connected successfully.", "success")
            return redirect(url_for("main.questions"))
        except DatabaseError as exc:
            flash(f"Connection failed: {exc}", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.pop("db_credentials", None)
    flash("Disconnected from database.", "info")
    return redirect(url_for("main.login"))


@bp.route("/questions")
def questions():
    if not _require_login():
        return redirect(url_for("main.login"))

    try:
        creds = _db_creds()
        users = list_users(creds)
        questions = list_user_questions(creds)
        return render_template("questions.html", users=users, questions=questions)
    except DatabaseError as exc:
        flash(f"Unable to load questions: {exc}", "danger")
        return redirect(url_for("main.login"))


@bp.route("/summary")
def summary():
    if not _require_login():
        return redirect(url_for("main.login"))

    user_id_raw = request.args.get("user_id", "").strip()
    start_date = request.args.get("start_date", "").strip() or None
    end_date = request.args.get("end_date", "").strip() or None

    user_id = int(user_id_raw) if user_id_raw else None

    try:
        creds = _db_creds()
        users = list_users(creds)
        summary_rows = list_daily_summary(
            creds,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        return render_template(
            "summary.html",
            users=users,
            summary_rows=summary_rows,
            selected_user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
    except DatabaseError as exc:
        flash(f"Unable to load summary: {exc}", "danger")
        return redirect(url_for("main.login"))


@bp.route("/questions/create", methods=["POST"])
def create_question():
    if not _require_login():
        return redirect(url_for("main.login"))

    form = request.form
    try:
        create_user_question(
            _db_creds(),
            user_id=int(form.get("user_id", 0)),
            question_text=form.get("question_text", "").strip(),
            question_type=form.get("question_type", "text"),
            is_active=bool(form.get("is_active")),
            sort_order=int(form.get("sort_order", 0)),
        )
        flash("Question created.", "success")
    except DatabaseError as exc:
        flash(f"Create failed: {exc}", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/questions/<int:question_id>/update", methods=["POST"])
def update_question(question_id: int):
    if not _require_login():
        return redirect(url_for("main.login"))

    form = request.form
    try:
        success = update_user_question(
            _db_creds(),
            question_id=question_id,
            question_text=form.get("question_text", "").strip(),
            question_type=form.get("question_type", "text"),
            is_active=bool(form.get("is_active")),
            sort_order=int(form.get("sort_order", 0)),
        )
        if success:
            flash("Question updated.", "success")
        else:
            flash("No question updated (check ID).", "warning")
    except DatabaseError as exc:
        flash(f"Update failed: {exc}", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/questions/<int:question_id>/delete", methods=["POST"])
def delete_question_route(question_id: int):
    if not _require_login():
        return redirect(url_for("main.login"))

    try:
        delete_user_question(_db_creds(), question_id=question_id)
        flash("Question deleted.", "info")
    except DatabaseError as exc:
        flash(f"Delete failed: {exc}", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/health")
def health():
    try:
        db = DatabaseConnection()
        db.call_procedure("health_check")
        db.close()
        return {"status": "healthy", "database": "connected"}, 200
    except DatabaseError as e:
        return {"status": "unhealthy", "error": str(e)}, 503
