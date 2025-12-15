"""
Simple script to read and execute schema.sql
"""

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def execute_schema():
    """Read and execute the schema.sql file."""
    # Read the schema file
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    # Connect to MySQL server
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
    )

    cursor = connection.cursor()

    # Execute each statement
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
                # Consume any results to avoid "Unread result found" error
                try:
                    cursor.fetchall()
                except mysql.connector.errors.InterfaceError:
                    print("No results to fetch.")
            except mysql.connector.Error as err:
                print(f"Error executing statement: {err}")
                print(f"Statement: {statement[:100]}...")
                raise

    connection.commit()
    cursor.close()
    connection.close()

    print("Schema executed successfully!")


if __name__ == "__main__":
    execute_schema()
