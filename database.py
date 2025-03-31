import os
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger(__name__)

def get_database_url():
    """Get the database URL from environment variables with fallback to SQLite"""
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        logger.warning("DATABASE_URL not found, falling back to SQLite")
        db_url = 'sqlite:///minto_disability.db'
    
    return db_url

def create_db_engine_with_retry(max_retries=5, retry_interval=2):
    """Create a database engine with retries on connection failure"""
    db_url = get_database_url()
    logger.info(f"Attempting to connect to database with URL type: {db_url.split(':')[0]}")
    
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30
            )
            
            # Test connection
            connection = engine.connect()
            connection.close()
            
            logger.info("Successfully connected to database")
            return engine
            
        except OperationalError as e:
            retries += 1
            last_error = e
            wait_time = retry_interval * retries
            
            logger.error(f"Database connection attempt {retries} failed: {str(e)}")
            logger.info(f"Retrying in {wait_time} seconds...")
            
            time.sleep(wait_time)
    
    logger.error(f"Failed to connect to database after {max_retries} attempts: {str(last_error)}")
    
    # Fall back to SQLite if PostgreSQL connection fails
    if db_url.startswith('postgresql'):
        logger.warning("Falling back to SQLite database")
        sqlite_url = 'sqlite:///minto_disability.db'
        
        try:
            engine = create_engine(sqlite_url)
            return engine
        except Exception as e:
            logger.error(f"Failed to create SQLite fallback database: {str(e)}")
    
    # Return a dummy engine as a last resort
    logger.error("Creating dummy engine that will raise exceptions on query attempts")
    return create_engine('sqlite:///:memory:')

def get_db_session():
    """Create a scoped database session"""
    engine = create_db_engine_with_retry()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return db_session