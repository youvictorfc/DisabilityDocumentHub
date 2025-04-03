import os
import logging
import mimetypes
from pathlib import Path
from flask import current_app
from app import db
from models import Document, DocumentChunk
from services.document.vector_service import add_to_vector_db
from services.ai.openai_service import get_openai_client, encode_image_to_base64

def is_image_file(file_path):
    """Check if a file is an image based on its extension or MIME type"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    extension = Path(file_path).suffix.lower()
    
    # Check by extension
    if extension in image_extensions:
        return True
    
    # Check by MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith('image/')

def extract_text_from_image(image_path):
    """
    Extract text content from an image using OCR via OpenAI's multimodal capabilities.
    """
    try:
        # Get the OpenAI client
        client = get_openai_client()
        
        # Encode the image to base64
        base64_image = encode_image_to_base64(image_path)
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an OCR assistant. Extract all visible text from the provided image. Maintain the formatting as much as possible."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text content from this image. Preserve paragraph structure and formatting as much as possible."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )
        
        extracted_text = response.choices[0].message.content
        current_app.logger.info(f"Extracted {len(extracted_text)} characters of text from image")
        return extracted_text
    
    except Exception as e:
        current_app.logger.error(f"Error extracting text from image: {str(e)}")
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_file(file_path):
    """
    Extract text content from a document file based on its type.
    Supports PDFs, text files, images, and docx files.
    """
    try:
        # Check if it's an image file
        if is_image_file(file_path):
            current_app.logger.info(f"Processing file as image: {file_path}")
            return extract_text_from_image(file_path)
        
        # File type handling
        if file_path.endswith('.pdf'):
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if the PDF contains images that might need OCR
                has_images = False
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    if '/XObject' in page['/Resources']:
                        has_images = True
                        break
                
                # If PDF has images and little text, it might be a scanned document
                # Try to use OpenAI Vision
                if has_images:
                    try:
                        # First try to extract text the normal way
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            extracted = page.extract_text()
                            if extracted:
                                text += extracted + "\n\n"
                        
                        # If we got very little text but have images, try OCR
                        if len(text.strip()) < 100 and has_images:
                            current_app.logger.info(f"PDF may be scanned, attempting OCR: {file_path}")
                            ocr_text = extract_text_from_image(file_path)
                            if ocr_text and len(ocr_text) > len(text):
                                return ocr_text
                    except Exception as e:
                        current_app.logger.warning(f"Error extracting text from PDF pages: {str(e)}")
                else:
                    # Regular PDF text extraction
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        extracted_text = page.extract_text()
                        if extracted_text:
                            text += extracted_text + "\n\n"
            
            return text
            
        elif file_path.endswith('.docx'):
            try:
                # Import the existing extract_docx functionality
                from extract_docx import extract_docx_content
                
                # Extract structured content from the DOCX
                structured_content = extract_docx_content(file_path)
                
                # Convert the structured content to plain text
                text_content = []
                
                # Add paragraphs
                for para in structured_content["paragraphs"]:
                    text_content.append(para)
                
                # Add tables in a readable format
                for i, table in enumerate(structured_content["tables"]):
                    text_content.append(f"\nTable {i+1}:")
                    for row in table:
                        text_content.append(" | ".join(row))
                    text_content.append("")  # Empty line after table
                
                return "\n".join(text_content)
            except Exception as docx_error:
                current_app.logger.error(f"Error extracting text from DOCX: {str(docx_error)}")
                # Try fallback to simpler method
                try:
                    import docx
                    doc = docx.Document(file_path)
                    full_text = []
                    for para in doc.paragraphs:
                        if para.text.strip():
                            full_text.append(para.text.strip())
                    return '\n'.join(full_text)
                except Exception as simple_error:
                    current_app.logger.error(f"Error in fallback DOCX extraction: {str(simple_error)}")
                    # Last resort fallback
                    return f"Content extracted from {os.path.basename(file_path)}"
            
        else:
            # Try to read as a text file
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except UnicodeDecodeError:
                # If it fails as text, try as binary/image
                current_app.logger.info(f"File could not be read as text, attempting as image: {file_path}")
                return extract_text_from_image(file_path)
    
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
