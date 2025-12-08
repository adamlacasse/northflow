import logging

import mysql.connector
from config import Config


class DatabaseError(Exception):
    """Raised when a database operation fails."""


class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DATABASE,
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Exception as e:
            logging.error(f"Database connection failed with error: {e}")
            raise DatabaseError(f"Database connection failed: {e}") from e

    def execute_query(self, query, params=()):
        """Execute a SELECT query and return results as list of dictionaries."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Database query failed with error: {e}")
            raise DatabaseError(f"Query failed: {e}") from e

    def call_procedure(self, proc_name, params=()):
        try:
            self.cursor.callproc(proc_name, params)
            results = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            return results
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
