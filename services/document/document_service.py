import os
import logging
from flask import current_app
from app import db
from models import Document, DocumentChunk
from services.document.vector_service import add_to_vector_db

def extract_text_from_file(file_path):
    """
    Extract text content from a document file based on its type.
    """
    try:
        # File type handling
        if file_path.endswith('.pdf'):
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            return text
            
        elif file_path.endswith('.docx'):
            # This is a placeholder - in a real app, you'd use python-docx
            return "This is sample content from a DOCX file for demonstration purposes."
            
        else:
            # Assume it's a text file
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
    
    except Exception as e:
        logging.error(f"Error extracting text: {str(e)}")
        raise Exception(f"Failed to extract text from file: {str(e)}")

def chunk_document(text, chunk_size=1000, overlap=200):
    """
    Split a document into overlapping chunks for processing.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # If we're not at the end, try to find a good breaking point
        if end < text_length:
            # Try to find a period, question mark, or exclamation point followed by a space or newline
            break_chars = ['. ', '? ', '! ', '.\n', '?\n', '!\n']
            best_break = end
            
            # Look for the best breaking point within the last 20% of the chunk
            for char in break_chars:
                pos = text.rfind(char, start + int(chunk_size * 0.8), end)
                if pos != -1 and pos + len(char) > best_break:
                    best_break = pos + len(char)
            
            end = best_break
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # Move the start position, accounting for overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks

def process_document(document_id):
    """
    Process a document for the knowledge base:
    1. Retrieve the document
    2. Split it into chunks
    3. Generate embeddings for each chunk
    4. Store in vector database
    """
    try:
        document = Document.query.get(document_id)
        if not document:
            raise Exception(f"Document with ID {document_id} not found")
        
        # Get document content
        content = document.content
        
        # Split into chunks
        chunks = chunk_document(content)
        
        # Process each chunk
        for i, chunk_text in enumerate(chunks):
            # Create database record for chunk
            chunk = DocumentChunk(
                document_id=document_id,
                content=chunk_text,
                chunk_index=i
            )
            db.session.add(chunk)
            db.session.flush()  # Get the ID without committing
            
            # Add to vector database
            embedding_id = add_to_vector_db(chunk.id, chunk_text)
            
            # Update chunk with embedding reference
            chunk.embedding_id = embedding_id
        
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing document: {str(e)}")
        raise Exception(f"Failed to process document: {str(e)}")
