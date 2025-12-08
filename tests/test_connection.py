#!/usr/bin/env python3
"""
Test script to verify database connection and DAL functionality.
Run from project root: python test_connection.py
"""

import logging
import sys
from dotenv import load_dotenv
from app.models import DatabaseConnection, DatabaseError

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    logging.info("Starting database connection test...")

    try:
        # Test database connection
        logging.info("Attempting to connect to database...")
        db = DatabaseConnection()
        logging.info("✓ Database connection successful!")

        # Test simple query
        logging.info("Testing query execution...")
        result = db.execute_query("SELECT DATABASE() as current_db")
        logging.info("✓ Query executed successfully!")
        logging.info(f"  Current database: {result[0]['current_db']}")

        # Test table existence
        logging.info("Checking for tables...")
        tables = db.execute_query("SHOW TABLES")
        if tables:
            logging.info(f"✓ Found {len(tables)} tables:")
            for table in tables:
                table_name = list(table.values())[0]
                logging.info(f"  - {table_name}")
        else:
            logging.warning("  No tables found. You may need to run schema.sql")

        # Clean up
        db.close()
        logging.info("✓ Connection closed successfully!")
        logging.info("\n🎉 All tests passed!")
        return 0

    except DatabaseError as e:
        logging.error(f"✗ Database error: {e}")
        logging.error("\nMake sure:")
        logging.error("  1. MySQL is running")
        logging.error("  2. Database 'northflow' exists (run src/database/schema.sql)")
        logging.error(
            "  3. Environment variables are set (DB_HOST, DB_USER, DB_PASSWORD)"
        )
        return 1
    except Exception as e:
        logging.error(f"✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
