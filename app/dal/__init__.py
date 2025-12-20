"""Data access layer (DAL) package.

All database connectivity and stored procedure calls should live here.
"""

from app.dal.database_connection import DatabaseConnection, DatabaseError

__all__ = ["DatabaseConnection", "DatabaseError"]
