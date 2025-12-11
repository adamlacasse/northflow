"""
Test suite for database connection and DAL functionality.
Run with: pytest tests/
"""

import pytest
from dotenv import load_dotenv

from app.models import DatabaseConnection, DatabaseError

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="module")
def db_connection():
    """Fixture to provide a database connection for tests."""
    db = DatabaseConnection()
    yield db
    db.close()


def test_database_connection():
    """Test that we can establish a database connection."""
    db = DatabaseConnection()
    assert db is not None
    assert db.connection is not None
    db.close()


def test_query_current_database(db_connection):
    """Test that we can execute a simple query to get current database."""
    result = db_connection.execute_query("SELECT DATABASE() as current_db")
    assert result is not None
    assert len(result) > 0
    assert result[0]["current_db"] == "northflow"


def test_show_tables(db_connection):
    """Test that we can query for tables in the database."""
    tables = db_connection.execute_query("SHOW TABLES")
    assert tables is not None
    assert isinstance(tables, list)
    # Note: This may be empty if schema hasn't been initialized


def test_connection_close():
    """Test that we can properly close a database connection."""
    db = DatabaseConnection()
    db.close()
    # Verify connection is closed by checking the connection state
    assert not db.connection.is_connected()


def test_database_error_on_invalid_query(db_connection):
    """Test that invalid queries raise DatabaseError."""
    with pytest.raises(DatabaseError):
        db_connection.execute_query("SELECT * FROM nonexistent_table_xyz123")
