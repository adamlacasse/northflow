"""Data access layer for user OAuth operations."""

from typing import Any, Dict, Optional

from app.dal.database_connection import DatabaseConnection, DatabaseError


def get_user_by_oauth(
    creds: Dict[str, Any], oauth_provider: str, oauth_id: str
) -> Optional[Dict[str, Any]]:
    """Find user by OAuth provider and ID.

    Args:
        creds: Database credentials
        oauth_provider: OAuth provider name ('google' or 'github')
        oauth_id: Provider's unique user ID

    Returns:
        User dict or None if not found
    """
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
        allow_raw_sql=True,
    )
    try:
        results = db.execute_query(
            "SELECT * FROM users WHERE oauth_provider = %s AND oauth_id = %s",
            (oauth_provider, oauth_id),
        )
        return results[0] if results else None
    finally:
        db.close()


def get_user_by_email(creds: Dict[str, Any], email: str) -> Optional[Dict[str, Any]]:
    """Find user by email address.

    Args:
        creds: Database credentials
        email: User email address

    Returns:
        User dict or None if not found
    """
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
        allow_raw_sql=True,
    )
    try:
        results = db.execute_query(
            "SELECT * FROM users WHERE email = %s",
            (email,),
        )
        return results[0] if results else None
    finally:
        db.close()


def create_oauth_user(
    creds: Dict[str, Any],
    *,
    oauth_provider: str,
    oauth_id: str,
    email: str,
    first_name: str = "",
    last_name: str = "",
) -> int:
    """Create a new OAuth user and return their ID.

    Args:
        creds: Database credentials
        oauth_provider: OAuth provider name ('google' or 'github')
        oauth_id: Provider's unique user ID
        email: User email address
        first_name: User's first name (optional)
        last_name: User's last name (optional)

    Returns:
        Newly created user ID

    Raises:
        DatabaseError: If user creation fails
    """
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
        allow_raw_sql=True,
    )
    try:
        db.execute_query(
            """INSERT INTO users
            (first_name, last_name, email, oauth_provider, oauth_id, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())""",
            (first_name, last_name, email, oauth_provider, oauth_id),
        )
        db.commit()

        # Fetch the newly created user to get their ID
        results = db.execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        )
        if results:
            return results[0]["id"]
        raise DatabaseError("Failed to retrieve newly created user ID")
    except Exception as exc:
        raise DatabaseError(f"Failed to create OAuth user: {exc}") from exc
    finally:
        db.close()


def update_last_login(creds: Dict[str, Any], user_id: int) -> None:
    """Update user's last login timestamp.

    Args:
        creds: Database credentials
        user_id: User ID

    Raises:
        DatabaseError: If update fails
    """
    db = DatabaseConnection(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        database=creds.get("database"),
        port=creds.get("port"),
        allow_raw_sql=True,
    )
    try:
        db.execute_query(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user_id,),
        )
        db.commit()
    except Exception as exc:
        raise DatabaseError(f"Failed to update last login: {exc}") from exc
    finally:
        db.close()
