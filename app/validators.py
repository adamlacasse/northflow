"""Input validation schemas and validators."""

from marshmallow import Schema, ValidationError, fields, validate


class QuestionSchema(Schema):
    """Schema for validating user question input."""

    question_text = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=500, error="Question must be 1-500 characters"),
        ],
    )
    question_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["text", "scale_1_5", "number", "boolean"],
            error="Invalid question type",
        ),
    )
    is_active = fields.Bool(load_default=True)
    sort_order = fields.Int(load_default=0, validate=validate.Range(min=0, max=1000))


class CheckinSchema(Schema):
    """Schema for validating check-in input."""

    notes = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=2000, error="Notes must be under 2000 characters"),
    )


class AnswerSchema(Schema):
    """Schema for validating answer input."""

    answer_text = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(
            max=2000, error="Answer must be under 2000 characters"
        ),
    )
    score = fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=5, error="Score must be between 0 and 5"),
    )


class SummaryFilterSchema(Schema):
    """Schema for validating summary filter parameters."""

    start_date = fields.Date(required=False, allow_none=True)
    end_date = fields.Date(required=False, allow_none=True)


def validate_form(
    schema_class: type, data: dict
) -> tuple[bool, dict | None, str | None]:
    """
    Validate form data against a schema.

    Args:
        schema_class: Marshmallow schema class
        data: Form data dict

    Returns:
        Tuple of (is_valid, cleaned_data, error_message)
    """
    schema = schema_class()
    try:
        cleaned = schema.load(data)
        return True, cleaned, None
    except ValidationError as e:
        # Flatten errors into a single message
        error_list = []
        for field, messages in e.messages.items():
            if isinstance(messages, list):
                error_list.extend(messages)
            else:
                error_list.append(str(messages))
        error_msg = "; ".join(error_list)
        return False, None, error_msg
