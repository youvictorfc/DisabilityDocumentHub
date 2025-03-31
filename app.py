import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from config import Config

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", Config.SECRET_KEY)

# Load configuration from Config class
app.config.from_object(Config)

# Configure database engine options
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy with app
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import and register blueprints
from controllers.auth_controller import auth_bp
from controllers.form_controller import form_bp
from controllers.policy_controller import policy_bp

app.register_blueprint(auth_bp)
app.register_blueprint(form_bp)
app.register_blueprint(policy_bp)

# Initialize database
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models
    
    try:
        # Create all tables with retry mechanism
        app.logger.info("Attempting to create database tables...")
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")
        app.logger.info("Application will continue without database initialization")

# Set up login manager loader
from models import User

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None

# Route for home page
@app.route('/')
def index():
    from flask import render_template, g
    
    # Set a flag in g to indicate if the database is accessible
    try:
        # Perform a simple query to check database connection
        from models import User
        User.query.limit(1).all()
        g.db_accessible = True
    except Exception as e:
        app.logger.error(f"Database connection error on index page: {str(e)}")
        g.db_accessible = False
    
    # Check if OpenAI API key is available
    from config import Config
    openai_api_key = Config.OPENAI_API_KEY
    
    return render_template('index.html', config={'OPENAI_API_KEY': openai_api_key})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
