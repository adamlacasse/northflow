"""Data access layer (DAL) package.

All database connectivity and stored procedure calls should live here.
"""

from app.dal.dal import DatabaseConnection, DatabaseError

__all__ = ["DatabaseConnection", "DatabaseError"]
