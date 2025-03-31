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
from controllers.admin_controller import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(form_bp)
app.register_blueprint(policy_bp)
app.register_blueprint(admin_bp)

# Initialize database
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models
    
    # Create all tables
    db.create_all()
    
    # Create necessary upload directories
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.FORM_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.DOCUMENT_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.PDF_OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
    os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'unsent_emails'), exist_ok=True)

# Set up login manager loader
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for home page
@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
