"""
Script to read and execute schema.sql with delimiter support.
"""

import os

import mysql.connector

from app.database.schema_utils import (
    execute_statement,
    get_db_connection,
    parse_schema_statements,
)


def execute_schema():
    """Read and execute the schema.sql file."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    statements = parse_schema_statements(schema_path)
    connection = get_db_connection()
    cursor = connection.cursor()

    for i, statement in enumerate(statements, 1):
        try:
            execute_statement(cursor, statement)
            print(f"Code block [{i}/{len(statements)}] OK")
        except mysql.connector.Error as err:
            print(f"Code block [{i}/{len(statements)}] ERROR: {err}")
            print(f"Statement: {statement[:100]}...")
            raise

    connection.commit()
    cursor.close()
    connection.close()
    print(f"\nSUCCESS: Schema executed successfully! ({len(statements)} statements)")


if __name__ == "__main__":
    execute_schema()
