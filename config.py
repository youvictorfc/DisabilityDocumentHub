import os

class Config:
    # Flask
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///minto_disability.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Vector DB settings
    VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_db')
    
    # Make sure the upload and vector DB directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    
    # Create subdirectories for different file types
    FORM_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'forms')
    DOCUMENT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'documents')
    PDF_OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, 'pdf_outputs')
    
    os.makedirs(FORM_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(DOCUMENT_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PDF_OUTPUT_FOLDER, exist_ok=True)
