import os
import logging
import traceback
from app import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Check if PostgreSQL environment variables are available
        pg_env_vars = ['PGHOST', 'PGUSER', 'PGPASSWORD', 'PGDATABASE', 'PGPORT', 'DATABASE_URL']
        missing_vars = [var for var in pg_env_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"Missing PostgreSQL environment variables: {', '.join(missing_vars)}")
            logger.info("Application may use SQLite as fallback if PostgreSQL connection fails")
        else:
            logger.info("All PostgreSQL environment variables are available")
        
        # Check OpenAI API key for AI features
        if not os.environ.get('OPENAI_API_KEY'):
            logger.warning("OPENAI_API_KEY environment variable is not set")
            logger.warning("AI-powered features may not function correctly")
        else:
            logger.info("OpenAI API key is available")
        
        # Start the Flask application
        logger.info("Starting Minto Disability Services Document Hub application")
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        logger.debug(traceback.format_exc())
        raise
