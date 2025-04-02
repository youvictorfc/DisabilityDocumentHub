from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    forms = db.relationship('FormResponse', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    structure = db.Column(db.Text)  # JSON structure of form questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete flag
    deleted_at = db.Column(db.DateTime, nullable=True)  # When the form was deleted
    
    # Relationships
    responses = db.relationship('FormResponse', backref='form', lazy=True)
    uploader = db.relationship('User', backref='uploaded_forms', lazy=True)
    
    def __repr__(self):
        return f'<Form {self.title}>'

class FormResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.Text)  # JSON structure of form answers
    is_complete = db.Column(db.Boolean, default=False)
    pdf_path = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FormResponse {self.id} for Form {self.form_id}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(50))  # e.g., policy, procedure
    file_path = db.Column(db.String(255))
    content = db.Column(db.Text)  # Raw text content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade="all, delete-orphan")
    uploader = db.relationship('User', backref='uploaded_documents', lazy=True)
    
    def __repr__(self):
        return f'<Document {self.title}>'

class DocumentChunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer)
    embedding_id = db.Column(db.String(255))  # Reference to vector embedding
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DocumentChunk {self.id} for Document {self.document_id}>'
