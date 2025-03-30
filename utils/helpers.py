import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions=None):
    """
    Check if a file has an allowed extension.
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx', 'txt'})
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """
    Generate a unique filename to prevent collisions.
    """
    # Get file extension
    _, ext = os.path.splitext(filename)
    
    # Generate unique filename with original extension
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    return unique_filename

def safe_file_save(file, folder, allowed_extensions=None):
    """
    Safely save a file with validation and unique filename.
    """
    if not file or file.filename == '':
        raise ValueError("No file provided")
    
    if not allowed_file(file.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions or current_app.config.get('ALLOWED_EXTENSIONS', []))}")
    
    # Create folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    
    # Generate secure and unique filename
    original_filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(original_filename)
    file_path = os.path.join(folder, unique_filename)
    
    # Save file
    file.save(file_path)
    
    return file_path

def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < (1024 * 1024):
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < (1024 * 1024 * 1024):
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_file_extension(filename):
    """
    Get the file extension from a filename.
    """
    return os.path.splitext(filename)[1].lower() if '.' in filename else ''

def chunk_text(text, max_length=1000, overlap=200):
    """
    Split text into chunks with overlap.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + max_length, text_length)
        
        # Try to find a good breaking point
        if end < text_length:
            # Look for period, question mark, or exclamation point
            for i in range(end, max(start, end - 100), -1):
                if text[i-1] in ['.', '!', '?'] and (i == text_length or text[i].isspace()):
                    end = i
                    break
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # Advance, considering overlap
        start = max(start + 1, end - overlap)
    
    return chunks
