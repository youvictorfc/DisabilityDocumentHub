"""
Migration runner script to execute all migrations in order
"""
import os
import importlib.util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migrations():
    """
    Run all migration scripts in the migrations directory
    """
    logger.info("Starting database migrations...")
    
    # Get the directory of this script
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files in the migrations directory except this one
    migration_files = [f for f in os.listdir(migrations_dir) 
                     if f.endswith('.py') and f != 'run_migrations.py' and f != '__init__.py']
    
    # Sort migration files to ensure they run in correct order
    migration_files.sort()
    
    logger.info(f"Found {len(migration_files)} migration scripts to run")
    
    for migration_file in migration_files:
        migration_path = os.path.join(migrations_dir, migration_file)
        logger.info(f"Running migration: {migration_file}")
        
        # Dynamically import and execute the migration script
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(
                f"migrations.{migration_file[:-3]}", migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            # Run the migration
            if hasattr(migration_module, 'run_migration'):
                migration_module.run_migration()
                logger.info(f"Migration completed successfully: {migration_file}")
            else:
                logger.warning(f"Migration script {migration_file} does not have a run_migration function")
        except Exception as e:
            logger.error(f"Error running migration {migration_file}: {str(e)}")
            raise
    
    logger.info("All migrations completed successfully")

if __name__ == "__main__":
    run_migrations()