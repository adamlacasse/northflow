import logging
from typing import Any

import mysql.connector

try:
    from config import Config
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    # Add project root to path if not already there
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from config import Config


class DatabaseError(Exception):
    """Raised when a database operation fails."""


class DatabaseConnection:
    def __init__(
        self,
        *,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        port: int | None = None,
        allow_raw_sql: bool = False,
    ):
        self.allow_raw_sql = allow_raw_sql
        try:
            self.connection = mysql.connector.connect(
                host=host or Config.DB_HOST,
                user=user or Config.DB_USER,
                password=password or Config.DB_PASSWORD,
                database=database or Config.DATABASE,
                port=port or 3306,
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Exception as e:
            logging.error(f"Database connection failed with error: {e}")
            raise DatabaseError(f"Database connection failed: {e}") from e

    def execute_query(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        if not self.allow_raw_sql:
            raise DatabaseError(
                """
                Raw SQL execution is disabled. Use stored
                procedures/views via call_procedure().
                """
            )
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()  # type: ignore[return-value]
        except Exception as e:
            logging.error(f"Database query failed with error: {e}")
            raise DatabaseError(f"Query failed: {e}") from e

    def call_procedure(
        self, proc_name: str, params: tuple = ()
    ) -> tuple[list[dict[str, Any]], tuple[Any, ...]]:
        """Execute a stored procedure, return result sets and updated params."""

        try:
            updated_params = tuple(self.cursor.callproc(proc_name, params))
            results: list[dict[str, Any]] = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            return results, updated_params
        except Exception as e:
            logging.error(f"Stored procedure call failed with error: {e}")
            logging.error(f"Procedure: {proc_name}, Parameters: {params}")
            raise DatabaseError(f"Stored procedure '{proc_name}' failed: {e}") from e

    def commit(self):
        try:
            self.connection.commit()
        except mysql.connector.Error as error:
            logging.error(f"Commit failed with error: {error}")
            logging.info("Rolling back transaction.")
            self.connection.rollback()
            raise DatabaseError(f"Commit failed: {error}") from error

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(f"Cursor or connection close failed with error: {e}")
