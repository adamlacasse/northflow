import os
import re
from typing import List, Tuple

from app.dal.database_connection import DatabaseConnection, DatabaseError
from app.database.schema_utils import parse_schema_statements

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# Object types we can safely re-apply in a repeatable manner.
# Note: MySQL does not support CREATE OR REPLACE for procedures/functions,
# so we drop then create.
_OBJECT_PATTERNS = [
    ("VIEW", re.compile(r"\bCREATE\s+VIEW\s+`?(\w+)`?", re.IGNORECASE)),
    ("PROCEDURE", re.compile(r"\bCREATE\s+PROCEDURE\s+`?(\w+)`?", re.IGNORECASE)),
    ("FUNCTION", re.compile(r"\bCREATE\s+FUNCTION\s+`?(\w+)`?", re.IGNORECASE)),
]


def _extract_objects(statements: List[str]) -> List[Tuple[str, str, str]]:
    """Return a list of (object_type, object_name, create_sql)."""
    objects: List[Tuple[str, str, str]] = []

    for stmt in statements:
        s = stmt.strip()
        if not s:
            continue

        for obj_type, pattern in _OBJECT_PATTERNS:
            match = pattern.search(s)
            if match:
                obj_name = match.group(1)
                objects.append((obj_type, obj_name, s))
                break

    return objects


def _drop_statement(obj_type: str, obj_name: str) -> str:
    """Return a DROP statement for the given object type/name."""
    if obj_type == "VIEW":
        return f"DROP VIEW IF EXISTS `{obj_name}`"
    if obj_type == "PROCEDURE":
        return f"DROP PROCEDURE IF EXISTS `{obj_name}`"
    if obj_type == "FUNCTION":
        return f"DROP FUNCTION IF EXISTS `{obj_name}`"
    raise ValueError(f"Unsupported object type: {obj_type}")


def main() -> None:
    """Apply repeatable schema objects (views/procedures/functions) from schema.sql."""
    try:
        # allow_raw_sql ensures we can run DDL directly for objects
        db = DatabaseConnection(allow_raw_sql=True)

        with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
            f.read()

        statements = parse_schema_statements(_SCHEMA_PATH)
        objects = _extract_objects(statements)

        if not objects:
            print("No schema objects (views/procedures/functions) found to apply.")
            return

        # Drop then create each object deterministically.
        for obj_type, obj_name, create_sql in objects:
            drop_sql = _drop_statement(obj_type, obj_name)
            db.cursor.execute(drop_sql)
            db.cursor.execute(create_sql)

        db.commit()
        print(f"Applied {len(objects)} schema objects successfully.")
    except (DatabaseError, OSError, ValueError):
        print("Error applying schema objects:")
        raise
    finally:
        try:
            db.close()  # type: ignore[name-defined]
        except Exception:
            pass


if __name__ == "__main__":
    main()
