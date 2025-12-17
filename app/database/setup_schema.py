"""
Simple script to read and execute schema.sql with delimiter support.
"""

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def _parse_line(line, delimiter, current_stmt, statements):
    """
    Parse a single line and update statement collection.
    Returns:
        tuple: (new_delimiter, should_clear_current_stmt)
    """
    # Handle delimiter changes
    if line.upper().startswith("DELIMITER"):
        _save_statement(statements, current_stmt)
        new_delimiter = line.split(None, 1)[1] if len(line.split()) > 1 else ";"
        return new_delimiter, True

    # Check if statement ends
    if line.endswith(delimiter):
        line_content = line[: -len(delimiter)].strip()
        if line_content:
            current_stmt.append(line_content)
        _save_statement(statements, current_stmt)
        return delimiter, True

    # Continue building statement
    current_stmt.append(line)
    return delimiter, False


def _save_statement(statements, stmt_lines):
    """Save a completed statement if non-empty."""
    stmt = "\n".join(stmt_lines).strip()
    if stmt:
        statements.append(stmt)


def _read_schema_file():
    """Read and parse schema.sql handling delimiter changes."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    statements = []
    current_stmt = []
    delimiter = ";"

    for line in lines:
        delimiter, should_clear = _parse_line(line, delimiter, current_stmt, statements)
        if should_clear:
            current_stmt = []

    # Save any remaining statement
    _save_statement(statements, current_stmt)
    return statements


def _get_db_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
    )


def _execute_statement(cursor, statement):
    """Execute a single SQL statement."""
    cursor.execute(statement)
    try:
        cursor.fetchall()
    except mysql.connector.errors.InterfaceError:
        pass  # No results to fetch


def execute_schema():
    """Read and execute the schema.sql file."""
    statements = _read_schema_file()
    connection = _get_db_connection()
    cursor = connection.cursor()

    for i, statement in enumerate(statements, 1):
        try:
            _execute_statement(cursor, statement)
            print(f"Code block [{i}/{len(statements)}] ✓")
        except mysql.connector.Error as err:
            print(f"Code block [{i}/{len(statements)}] ✗ Error: {err}")
            print(f"Statement: {statement[:100]}...")
            raise

    connection.commit()
    cursor.close()
    connection.close()
    print(f"\n✓ Schema executed successfully! ({len(statements)} statements)")


if __name__ == "__main__":
    execute_schema()
