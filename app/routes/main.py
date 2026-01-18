"""Main routes blueprint."""

import logging
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

from app import limiter
from app.dal import DatabaseConnection, DatabaseError
from app.routes.auth import login_required
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
    update_user_question,
)
from app.validators import (
    AnswerSchema,
    CheckinSchema,
    QuestionSchema,
    SummaryFilterSchema,
    validate_form,
)
from config import Config

bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


def _db_creds() -> Dict[str, Any]:
    """Get database credentials from environment (always server-side)."""
    return {
        "host": Config.DB_HOST,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "database": Config.DATABASE,
        "port": Config.DB_PORT,
    }


def _get_current_user() -> int:
    """Get current user ID from session.

    Returns the authenticated user's ID from the session.
    This is set during OAuth login in app/routes/auth.py.

    Returns:
        int: The current user's ID from session['user_id']
    """
    return session.get("user_id")


@bp.route("/")
@login_required
def index():
    """Entry route. Redirect to questions page."""
    return redirect(url_for("main.questions"))


@bp.route("/questions")
@login_required
def questions():
    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        questions = list_user_questions(creds)
        # Filter to only show current user's questions
        my_questions = [q for q in questions if q["user_id"] == current_user_id]
        return render_template("questions.html", questions=my_questions)
    except DatabaseError as exc:
        logger.error(f"Database error loading questions: {exc}", exc_info=True)
        flash(
            "Unable to load questions. Please try again.",
            "danger",
        )
        return render_template("questions.html", questions=[])


@bp.route("/summary")
@login_required
def summary():
    start_date = request.args.get("start_date", "").strip() or None
    end_date = request.args.get("end_date", "").strip() or None

    try:
        # Validate date parameters
        is_valid, cleaned, error_msg = validate_form(
            SummaryFilterSchema, {"start_date": start_date, "end_date": end_date}
        )
        if not is_valid:
            flash(f"Invalid filters: {error_msg}", "warning")
            cleaned = {}

        creds = _db_creds()
        current_user_id = _get_current_user()
        summary_rows = list_daily_summary(
            creds,
            user_id=current_user_id,
            start_date=cleaned.get("start_date") if is_valid else start_date,
            end_date=cleaned.get("end_date") if is_valid else end_date,
        )
        return render_template(
            "summary.html",
            summary_rows=summary_rows,
            start_date=start_date,
            end_date=end_date,
        )
    except DatabaseError as exc:
        logger.error(f"Database error loading summary: {exc}", exc_info=True)
        flash("Unable to load summary. Please try again.", "danger")
        return render_template("summary.html", summary_rows=[])


@bp.route("/questions/create", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def create_question():
    logger.info(f"create_question called. Session user_id: {session.get('user_id')}")
    form_data = {
        "question_text": request.form.get("question_text", "").strip(),
        "question_type": request.form.get("question_type", "text"),
        "is_active": bool(request.form.get("is_active")),
        "sort_order": request.form.get("sort_order", "0"),
    }

    # Validate input
    is_valid, cleaned, error_msg = validate_form(QuestionSchema, form_data)
    if not is_valid:
        flash(f"Invalid question: {error_msg}", "danger")
        return redirect(url_for("main.questions"))

    try:
        create_user_question(
            _db_creds(),
            user_id=_get_current_user(),
            question_text=cleaned["question_text"],
            question_type=cleaned["question_type"],
            is_active=cleaned["is_active"],
            sort_order=int(cleaned["sort_order"]),
        )
        flash("Question created.", "success")
    except DatabaseError as exc:
        logger.error(f"Database error creating question: {exc}", exc_info=True)
        flash("Unable to create question. Please try again.", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/questions/<int:question_id>/update", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def update_question(question_id: int):
    form_data = {
        "question_text": request.form.get("question_text", "").strip(),
        "question_type": request.form.get("question_type", "text"),
        "is_active": bool(request.form.get("is_active")),
        "sort_order": request.form.get("sort_order", "0"),
    }

    # Validate input
    is_valid, cleaned, error_msg = validate_form(QuestionSchema, form_data)
    if not is_valid:
        flash(f"Invalid question: {error_msg}", "danger")
        return redirect(url_for("main.questions"))

    try:
        success = update_user_question(
            _db_creds(),
            question_id=question_id,
            question_text=cleaned["question_text"],
            question_type=cleaned["question_type"],
            is_active=cleaned["is_active"],
            sort_order=int(cleaned["sort_order"]),
        )
        if success:
            flash("Question updated.", "success")
        else:
            flash("Question not found.", "warning")
    except DatabaseError as exc:
        logger.error(f"Database error updating question: {exc}", exc_info=True)
        flash("Unable to update question. Please try again.", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def delete_question_route(question_id: int):
    try:
        delete_user_question(_db_creds(), question_id=question_id)
        flash("Question deleted.", "info")
    except DatabaseError as exc:
        logger.error(f"Database error deleting question: {exc}", exc_info=True)
        flash("Unable to delete question. Please try again.", "danger")

    return redirect(url_for("main.questions"))


@bp.route("/checkins")
@login_required
def checkins():
    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        checkins_list = list_checkins(creds, user_id=current_user_id)

        return render_template(
            "checkins.html",
            checkins=checkins_list,
        )
    except DatabaseError as exc:
        logger.error(f"Database error loading check-ins: {exc}", exc_info=True)
        flash("Unable to load check-ins. Please try again.", "danger")
        return render_template("checkins.html", checkins=[])


@bp.route("/checkins/create", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def create_checkin_route():
    form_data = {"notes": request.form.get("notes", "").strip()}

    # Validate input
    is_valid, cleaned, error_msg = validate_form(CheckinSchema, form_data)
    if not is_valid:
        flash(f"Invalid check-in: {error_msg}", "danger")
        return redirect(url_for("main.checkins"))

    try:
        checkin_id = create_checkin(
            _db_creds(),
            user_id=_get_current_user(),
            notes=cleaned.get("notes"),
        )
        flash("Check-in created. Add your answers below.", "success")
        return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))
    except DatabaseError as exc:
        logger.error(f"Database error creating check-in: {exc}", exc_info=True)
        flash("Unable to create check-in. Please try again.", "danger")
        return redirect(url_for("main.checkins"))


@bp.route("/checkins/<int:checkin_id>")
@login_required
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
        logger.error(f"Database error loading check-in: {exc}", exc_info=True)
        flash("Unable to load check-in. Please try again.", "danger")
        return render_template(
            "checkin_detail.html", checkin={}, questions=[], answers={}
        )


@bp.route("/checkins/<int:checkin_id>/update", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def update_checkin_route(checkin_id: int):
    form_data = {"notes": request.form.get("notes", "").strip()}

    # Validate input
    is_valid, cleaned, error_msg = validate_form(CheckinSchema, form_data)
    if not is_valid:
        flash(f"Invalid notes: {error_msg}", "danger")
        return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))

    try:
        success = update_checkin(
            _db_creds(),
            checkin_id=checkin_id,
            notes=cleaned.get("notes"),
        )
        if success:
            flash("Check-in notes updated.", "success")
        else:
            flash("Check-in not found.", "warning")
    except DatabaseError as exc:
        logger.error(f"Database error updating check-in: {exc}", exc_info=True)
        flash("Unable to update check-in. Please try again.", "danger")

    return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))


@bp.route("/checkins/<int:checkin_id>/delete", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def delete_checkin_route(checkin_id: int):
    try:
        delete_checkin(_db_creds(), checkin_id=checkin_id)
        flash("Check-in deleted.", "info")
        return redirect(url_for("main.checkins"))
    except DatabaseError as exc:
        logger.error(f"Database error deleting check-in: {exc}", exc_info=True)
        flash("Unable to delete check-in. Please try again.", "danger")
        return redirect(url_for("main.checkins"))


@bp.route("/checkins/<int:checkin_id>/answers/<int:question_id>/save", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def save_answer_route(checkin_id: int, question_id: int):
    form_data = {
        "answer_text": request.form.get("answer_text", "").strip() or None,
        "score": request.form.get("score", "").strip() or None,
    }

    # Validate input
    is_valid, cleaned, error_msg = validate_form(AnswerSchema, form_data)
    if not is_valid:
        flash(f"Invalid answer: {error_msg}", "danger")
        return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))

    try:
        add_answer(
            _db_creds(),
            checkin_id=checkin_id,
            question_id=question_id,
            answer_text=cleaned.get("answer_text"),
            score=cleaned.get("score"),
        )
        flash("Answer saved.", "success")
    except DatabaseError as exc:
        logger.error(f"Database error saving answer: {exc}", exc_info=True)
        flash("Unable to save answer. Please try again.", "danger")

    return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))


@bp.route(
    "/checkins/<int:checkin_id>/answers/<int:question_id>/delete", methods=["POST"]
)
@limiter.limit("10/minute")
@login_required
def delete_answer_route(checkin_id: int, question_id: int):
    try:
        delete_answer(
            _db_creds(),
            checkin_id=checkin_id,
            question_id=question_id,
        )
        flash("Answer deleted.", "info")
    except DatabaseError as exc:
        logger.error(f"Database error deleting answer: {exc}", exc_info=True)
        flash("Unable to delete answer. Please try again.", "danger")

    return redirect(url_for("main.checkin_detail", checkin_id=checkin_id))


@bp.route("/health")
def health():
    try:
        db = DatabaseConnection()
        db.call_procedure("health_check")
        db.close()
        return {"status": "healthy", "database": "connected"}, 200
    except DatabaseError as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"status": "unhealthy", "error": "Database connection failed"}, 503
