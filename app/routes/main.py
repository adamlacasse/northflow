"""Main routes blueprint."""

import logging
from typing import Any, Dict

import mysql.connector
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
from app.dal import DatabaseError
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

MAIN_QUESTIONS = "main.questions"
CHECKIN_DETAIL = "checkin_detail.html"
MAIN_CHECKIN_DETAIL = "main.checkin_detail"


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
    return redirect(url_for(MAIN_QUESTIONS))


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
        return render_template(
            "summary.html",
            summary_rows=[],
            start_date=start_date,
            end_date=end_date,
        )


@bp.route("/checkins")
@login_required
def checkins():
    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        checkins = list_checkins(creds, user_id=current_user_id)
        return render_template("checkins.html", checkins=checkins)
    except DatabaseError as exc:
        logger.error(f"Database error loading checkins: {exc}", exc_info=True)
        flash("Unable to load check-ins. Please try again.", "danger")
        return render_template("checkins.html", checkins=[])


@bp.route("/checkins/new", methods=["GET", "POST"])
@limiter.limit("10/minute")
@login_required
def new_checkin():
    if request.method == "POST":
        form_data = request.form.to_dict(flat=True)
        is_valid, cleaned, error_msg = validate_form(CheckinSchema, form_data)

        if not is_valid:
            flash(error_msg, "danger")
            return render_template(CHECKIN_DETAIL, checkin=None, answers=[])

        try:
            creds = _db_creds()
            current_user_id = _get_current_user()
            checkin_id = create_checkin(
                creds,
                user_id=current_user_id,
                notes=cleaned.get("notes"),
            )
            flash("Check-in created.", "success")
            return redirect(url_for(MAIN_CHECKIN_DETAIL, checkin_id=checkin_id))
        except DatabaseError as exc:
            logger.error(f"Database error creating checkin: {exc}", exc_info=True)
            flash("Unable to create check-in. Please try again.", "danger")
            return render_template(CHECKIN_DETAIL, checkin=None, answers=[])

    # GET
    return render_template(CHECKIN_DETAIL, checkin=None, answers=[])


@bp.route("/checkins/<int:checkin_id>")
@login_required
def checkin_detail(checkin_id: int):
    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        checkin = get_checkin(creds, checkin_id=checkin_id, user_id=current_user_id)
        answers = get_checkin_answers(creds, checkin_id=checkin_id)
        return render_template(
            CHECKIN_DETAIL,
            checkin=checkin,
            answers=answers,
        )
    except DatabaseError as exc:
        logger.error(f"Database error loading checkin: {exc}", exc_info=True)
        flash("Unable to load check-in. Please try again.", "danger")
        return redirect(url_for("main.checkins"))


@bp.route("/checkins/<int:checkin_id>/edit", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def edit_checkin(checkin_id: int):
    form_data = request.form.to_dict(flat=True)
    is_valid, cleaned, error_msg = validate_form(CheckinSchema, form_data)

    if not is_valid:
        flash(error_msg, "danger")
        return redirect(url_for(MAIN_CHECKIN_DETAIL, checkin_id=checkin_id))

    try:
        creds = _db_creds()
        update_checkin(
            creds,
            checkin_id=checkin_id,
            notes=cleaned.get("notes"),
        )
        flash("Check-in updated.", "success")
    except DatabaseError as exc:
        logger.error(f"Database error updating checkin: {exc}", exc_info=True)
        flash("Unable to update check-in. Please try again.", "danger")

    return redirect(url_for(MAIN_CHECKIN_DETAIL, checkin_id=checkin_id))


@bp.route("/checkins/<int:checkin_id>/delete", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def delete_checkin_route(checkin_id: int):
    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        delete_checkin(creds, checkin_id=checkin_id, user_id=current_user_id)
        flash("Check-in deleted.", "info")
    except DatabaseError as exc:
        logger.error(f"Database error deleting checkin: {exc}", exc_info=True)
        flash("Unable to delete check-in. Please try again.", "danger")

    return redirect(url_for("main.checkins"))


@bp.route("/questions/new", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def new_question():
    form_data = request.form.to_dict(flat=True)
    form_data["is_active"] = "is_active" in request.form
    is_valid, cleaned, error_msg = validate_form(QuestionSchema, form_data)

    if not is_valid:
        flash(error_msg, "danger")
        return redirect(url_for(MAIN_QUESTIONS))

    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        create_user_question(
            creds,
            user_id=current_user_id,
            question_text=cleaned.get("question_text"),
            question_type=cleaned.get("question_type"),
            is_active=cleaned.get("is_active"),
            sort_order=cleaned.get("sort_order"),
        )
        flash("Question added.", "success")
    except DatabaseError as exc:
        logger.error(f"Database error creating question: {exc}", exc_info=True)
        flash("Unable to add question. Please try again.", "danger")

    return redirect(url_for(MAIN_QUESTIONS))


@bp.route("/questions/<int:question_id>/edit", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def edit_question(question_id: int):
    form_data = request.form.to_dict(flat=True)
    form_data["is_active"] = "is_active" in request.form
    is_valid, cleaned, error_msg = validate_form(QuestionSchema, form_data)

    if not is_valid:
        flash(error_msg, "danger")
        return redirect(url_for(MAIN_QUESTIONS))

    try:
        creds = _db_creds()
        update_user_question(
            creds,
            question_id=question_id,
            question_text=cleaned.get("question_text"),
            question_type=cleaned.get("question_type"),
            is_active=cleaned.get("is_active"),
            sort_order=cleaned.get("sort_order"),
        )
        flash("Question updated.", "success")
    except DatabaseError as exc:
        logger.error(f"Database error updating question: {exc}", exc_info=True)
        flash("Unable to update question. Please try again.", "danger")

    return redirect(url_for(MAIN_QUESTIONS))


@bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def delete_question_route(question_id: int):
    try:
        creds = _db_creds()
        current_user_id = _get_current_user()
        delete_user_question(
            creds,
            question_id=question_id,
            user_id=current_user_id,
        )
        flash("Question deleted.", "info")
    except DatabaseError as exc:
        logger.error(f"Database error deleting question: {exc}", exc_info=True)
        flash("Unable to delete question. Please try again.", "danger")

    return redirect(url_for(MAIN_QUESTIONS))


@bp.route("/checkins/<int:checkin_id>/answers/<int:question_id>", methods=["POST"])
@limiter.limit("10/minute")
@login_required
def save_answer(checkin_id: int, question_id: int):
    form_data = request.form.to_dict(flat=True)
    is_valid, cleaned, error_msg = validate_form(AnswerSchema, form_data)

    if not is_valid:
        flash(error_msg, "danger")
        return redirect(url_for(MAIN_CHECKIN_DETAIL, checkin_id=checkin_id))

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

    return redirect(url_for(MAIN_CHECKIN_DETAIL, checkin_id=checkin_id))


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

    return redirect(url_for(MAIN_CHECKIN_DETAIL, checkin_id=checkin_id))


@bp.route("/health")
def health():
    """Health/readiness endpoint.

    We treat DB connectivity and schema readiness as separate concerns. If the
    required routines haven't been applied yet, we return 503 so the service
    won't be considered ready.
    """
    conn = None
    cursor = None
    try:
        # Use a direct MySQL connection so we can distinguish:
        # - DB unreachable vs
        # - routine missing (schema not ready)
        conn = mysql.connector.connect(**_db_creds())
        cursor = conn.cursor()

        # "health_check" should exist after bootstrap/apply objects.
        cursor.callproc("health_check")
        return {"status": "healthy", "database": "connected"}, 200
    except mysql.connector.Error as exc:
        # 1305 = ER_SP_DOES_NOT_EXIST (procedure does not exist)
        if getattr(exc, "errno", None) == 1305:
            logger.error(f"Health check failed: schema not ready: {exc}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": "Schema not ready (required routines missing)",
            }, 503

        logger.error(f"Health check failed: {exc}", exc_info=True)
        return {"status": "unhealthy", "error": "Database connection failed"}, 503
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
