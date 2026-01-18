"""Main routes blueprint."""

from typing import Any, Dict

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.dal import DatabaseConnection, DatabaseError
from app.services.answers import (
    add_answer,
    delete_answer,
    get_checkin_answers,
)
from app.services.checkins import (
    create_checkin,
    delete_checkin,
    get_checkin,
    list_checkins,
    update_checkin,
)
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
    """Get database credentials from environment (always server-side)."""
    return {
        "host": Config.DB_HOST,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "database": Config.DATABASE,
        "port": Config.DB_PORT,
    }


@bp.route("/")
def index():
    """Entry route. Redirect to questions page."""
    return redirect(url_for("main.questions"))


@bp.route("/questions")
def questions():
    try:
        creds = _db_creds()
        users = list_users(creds)
        questions = list_user_questions(creds)
        return render_template("questions.html", users=users, questions=questions)
    except DatabaseError as exc:
        flash(f"Unable to load questions: {exc}", "danger")
        return render_template("questions.html", users=[], questions=[])


@bp.route("/summary")
def summary():
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
        return render_template("summary.html", users=[], summary_rows=[])


@bp.route("/questions/create", methods=["POST"])
def create_question():
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
    try:
        delete_user_question(_db_creds(), question_id=question_id)
        flash("Question deleted.", "info")
    except DatabaseError as exc:
        flash(f"Delete failed: {exc}", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/checkins")
def checkins():
    user_id_raw = request.args.get("user_id", "").strip()
    user_id = int(user_id_raw) if user_id_raw else None

    try:
        creds = _db_creds()
        users = list_users(creds)

        if user_id:
            checkins_list = list_checkins(creds, user_id=user_id)
        else:
            checkins_list = []

        return render_template(
            "checkins.html",
            users=users,
            checkins=checkins_list,
            selected_user_id=user_id,
        )
    except DatabaseError as exc:
        flash(f"Unable to load check-ins: {exc}", "danger")
        return render_template("checkins.html", users=[], checkins=[])


@bp.route("/checkins/create", methods=["POST"])
def create_checkin_route():
    form = request.form
    user_id = int(form.get("user_id", 0))
    notes = form.get("notes", "").strip()

    try:
        checkin_id = create_checkin(
            _db_creds(),
            user_id=user_id,
            notes=notes,
        )
        flash("Check-in created. Add your answers below.", "success")
        return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))
    except DatabaseError as exc:
        flash(f"Create check-in failed: {exc}", "danger")
        return redirect(url_for("main.checkins", user_id=user_id))


@bp.route("/checkins/<int:checkin_id>")
def checkin_detail(checkin_id: int):
    try:
        creds = _db_creds()
        checkin = get_checkin(creds, checkin_id=checkin_id)
        if not checkin:
            flash("Check-in not found.", "warning")
            return redirect(url_for("main.checkins"))

        user_id = checkin.get("user_id")
        user_questions = list_user_questions(creds)
        # Filter to active questions for this user
        user_qs = [
            q for q in user_questions if q["user_id"] == user_id and q["is_active"]
        ]

        answers = get_checkin_answers(creds, checkin_id=checkin_id)
        answers_dict = {a["question_id"]: a for a in answers}

        return render_template(
            "checkin_detail.html",
            checkin=checkin,
            questions=user_qs,
            answers=answers_dict,
        )
    except DatabaseError as exc:
        flash(f"Unable to load check-in: {exc}", "danger")
        return render_template(
            "checkin_detail.html", checkin={}, questions=[], answers={}
        )


@bp.route("/checkins/<int:checkin_id>/update", methods=["POST"])
def update_checkin_route(checkin_id: int):
    form = request.form
    notes = form.get("notes", "").strip()

    try:
        success = update_checkin(
            _db_creds(),
            checkin_id=checkin_id,
            notes=notes,
        )
        if success:
            flash("Check-in notes updated.", "success")
        else:
            flash("Check-in not found.", "warning")
    except DatabaseError as exc:
        flash(f"Update failed: {exc}", "danger")

    return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))


@bp.route("/checkins/<int:checkin_id>/delete", methods=["POST"])
def delete_checkin_route(checkin_id: int):
    try:
        checkin = get_checkin(_db_creds(), checkin_id=checkin_id)
        user_id = checkin.get("user_id") if checkin else None
        delete_checkin(_db_creds(), checkin_id=checkin_id)
        flash("Check-in deleted.", "info")
        if user_id:
            return redirect(url_for("main.checkins", user_id=user_id))
        return redirect(url_for("main.checkins"))
    except DatabaseError as exc:
        flash(f"Delete failed: {exc}", "danger")
        return redirect(url_for("main.checkins"))


@bp.route("/checkins/<int:checkin_id>/answers/<int:question_id>/save", methods=["POST"])
def save_answer_route(checkin_id: int, question_id: int):
    form = request.form
    answer_text = form.get("answer_text", "").strip() or None
    score_raw = form.get("score", "").strip()
    score = float(score_raw) if score_raw else None

    try:
        add_answer(
            _db_creds(),
            checkin_id=checkin_id,
            question_id=question_id,
            answer_text=answer_text,
            score=score,
        )
        flash("Answer saved.", "success")
    except DatabaseError as exc:
        flash(f"Save answer failed: {exc}", "danger")

    return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))


@bp.route(
    "/checkins/<int:checkin_id>/answers/<int:question_id>/delete", methods=["POST"]
)
def delete_answer_route(checkin_id: int, question_id: int):
    try:
        delete_answer(
            _db_creds(),
            checkin_id=checkin_id,
            question_id=question_id,
        )
        flash("Answer deleted.", "info")
    except DatabaseError as exc:
        flash(f"Delete answer failed: {exc}", "danger")

    return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))


@bp.route("/health")
def health():
    try:
        db = DatabaseConnection()
        db.call_procedure("health_check")
        db.close()
        return {"status": "healthy", "database": "connected"}, 200
    except DatabaseError as e:
        return {"status": "unhealthy", "error": str(e)}, 503
