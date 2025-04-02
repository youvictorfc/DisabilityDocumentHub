"""
Migration script to add original_text column to the form table
"""
import logging
import os
import sys

# Add the parent directory to sys.path so we can import from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from app import db
from sqlalchemy import Text
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

def run_migration():
    """
    Run the migration to add the original_text column to the form table
    if it doesn't already exist.
    """
    try:
        with app.app_context():
            # Check if the column already exists
            conn = db.engine.connect()
            result = conn.execute(text("SELECT * FROM information_schema.columns WHERE table_name='form' AND column_name='original_text'"))
            if result.rowcount == 0:
                logger.info("Adding original_text column to form table...")
                # Add the column if it doesn't exist
                conn.execute(text("ALTER TABLE form ADD COLUMN original_text TEXT"))
                conn.commit()
                logger.info("Successfully added original_text column to form table")
            else:
                logger.info("original_text column already exists in form table")
            conn.close()
    except Exception as e:
        logger.error(f"Error in migration: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()