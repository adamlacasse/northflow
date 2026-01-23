import os
from typing import Iterable

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def _strip_inline_comment(line: str) -> str:
    if "--" in line:
        return line.split("--", 1)[0].rstrip()
    return line


def _read_schema_lines(schema_path: str) -> list[str]:
    lines: list[str] = []
    with open(schema_path, "r", encoding="utf-8") as file_handle:
        for raw_line in file_handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("--"):
                continue
            line = _strip_inline_comment(line)
            if not line:
                continue
            lines.append(line)
    return lines


def _save_statement(statements: list[str], stmt_lines: Iterable[str]) -> None:
    stmt = "\n".join(stmt_lines).strip()
    if stmt:
        statements.append(stmt)


def _parse_delimiter(line: str) -> str:
    parts = line.split()
    if len(parts) > 1:
        return parts[1]
    return ";"


def parse_schema_statements(schema_path: str) -> list[str]:
    """Read schema.sql and return parsed statements with delimiter support."""
    lines = _read_schema_lines(schema_path)
    statements: list[str] = []
    current_stmt: list[str] = []
    delimiter = ";"

    for line in lines:
        if line.upper().startswith("DELIMITER"):
            _save_statement(statements, current_stmt)
            delimiter = _parse_delimiter(line)
            current_stmt = []
            continue

        if line.endswith(delimiter):
            line_content = line[: -len(delimiter)].strip()
            if line_content:
                current_stmt.append(line_content)
            _save_statement(statements, current_stmt)
            current_stmt = []
            continue

        current_stmt.append(line)

    _save_statement(statements, current_stmt)
    return statements


def _coerce_port(port_raw: str | None) -> int:
    try:
        return int(port_raw or "3306")
    except ValueError:
        return 3306


def get_db_connection(database: str | None = None) -> mysql.connector.MySQLConnection:
    """Create and return a database connection."""
    port = _coerce_port(os.getenv("DB_PORT"))
    kwargs: dict[str, object] = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD"),
        "port": port,
    }
    if database:
        kwargs["database"] = database
    return mysql.connector.connect(**kwargs)


def execute_statement(
    cursor: mysql.connector.cursor.MySQLCursor, statement: str
) -> None:
    """Execute a single SQL statement."""
    cursor.execute(statement)
    try:
        cursor.fetchall()
    except mysql.connector.errors.InterfaceError:
        pass
