"""
Apply views and stored procedures from schema.sql without dropping tables.
"""

import os
import re

import mysql.connector

from app.database.schema_utils import (
    execute_statement,
    get_db_connection,
    parse_schema_statements,
)

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
_OBJECT_PATTERNS = [
    ("VIEW", re.compile(r"\bCREATE\s+VIEW\s+`?(\w+)`?", re.IGNORECASE)),
    ("PROCEDURE", re.compile(r"\bCREATE\s+PROCEDURE\s+`?(\w+)`?", re.IGNORECASE)),
]


def _detect_object(statement: str) -> tuple[str, str] | None:
    for object_type, pattern in _OBJECT_PATTERNS:
        match = pattern.search(statement)
        if match:
            return object_type, match.group(1)
    return None


def apply_schema_objects():
    statements = parse_schema_statements(_SCHEMA_PATH)
    db_name = os.getenv("DB_NAME") or os.getenv("DATABASE") or "northflow"
    connection = get_db_connection(database=db_name)
    cursor = connection.cursor()

    total = 0
    try:
        for statement in statements:
            detected = _detect_object(statement)
            if not detected:
                continue
            object_type, object_name = detected
            total += 1
            try:
                cursor.execute(f"DROP {object_type} IF EXISTS `{object_name}`")
                execute_statement(cursor, statement)
                print(f"{object_type} `{object_name}` OK")
            except mysql.connector.Error as err:
                print(f"{object_type} `{object_name}` ERROR: {err}")
                print(f"Statement: {statement[:100]}...")
                raise

        connection.commit()
    finally:
        cursor.close()
        connection.close()

    print(f"\nSUCCESS: Applied {total} schema objects.")


if __name__ == "__main__":
    apply_schema_objects()
