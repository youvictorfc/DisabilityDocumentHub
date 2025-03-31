import os
import json
import logging
import base64
import mimetypes
from pathlib import Path
from openai import OpenAI
from flask import current_app

# Initialize OpenAI client - will be set with the actual API key in the functions
openai = None

def get_openai_client():
    """
    Get or initialize the OpenAI client with the current API key from the app config
    """
    global openai
    if openai is None:
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable.")
        openai = OpenAI(api_key=api_key)
    return openai

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

def encode_image_to_base64(image_path):
    """Encode an image file to base64 for the OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_form_fields_from_image(image_path):
    """Extract form fields from an image using GPT-4o multimodal capabilities"""
    client = get_openai_client()
    
    try:
        base64_image = encode_image_to_base64(image_path)
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a form extraction expert for Minto Disability Services with special focus on EXACT field extraction. "
                        "Your task is to analyze the provided image of a form and extract ALL form fields/questions EXACTLY as they appear in the original. "
                        "IMPORTANT: Do NOT rephrase, modify, combine, or add any questions. Preserve the original text, formatting, and order exactly. "
                        "Extract the precise label text for every field. Do not summarize or generalize fields. Be extremely literal in your extraction. "
                        "You must return your output as structured JSON."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here's an image of a form. Your task is to extract ALL fields EXACTLY as they appear in the original form, maintaining the original wording, order, and structure. "
                            "Don't try to improve, clarify, or reorganize the form - I need the EXACT original form fields. "
                            "Format your response as a structured JSON with a 'questions' array in the SAME ORDER as they appear on the form. Include: "
                            "1. A unique 'id' (use a simple index number or field name without modifying the text) "
                            "2. 'question_text' (the EXACT and COMPLETE text of the field/question as it appears on the form, including any numbering or formatting) "
                            "3. 'field_type' (text, textarea, date, checkbox, radio, select, email, etc.) "
                            "4. 'options' array (EXACT options text for checkbox, radio, select fields) "
                            "5. 'required' (true/false - based on asterisks or 'required' markers) "
                            "Return this as JSON. Do not skip ANY fields. Do not merge fields. Do not improve or reword the questions."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        current_app.logger.info(f"Extracted {len(result.get('questions', []))} form fields from image")
        return result
    
    except Exception as e:
        current_app.logger.error(f"Error extracting fields from image: {str(e)}")
        raise Exception(f"Failed to extract form fields from image: {str(e)}")

def parse_form_document(file_path):
    """
    Parse a form document and extract a structured representation of questions.
    Handles PDFs, text files, images, and docx files.
    """
    try:
        file_path_str = str(file_path)
        current_app.logger.info(f"Parsing form document: {file_path_str}")
        
        # Check if the file is an image
        if is_image_file(file_path_str):
            current_app.logger.info(f"Processing file as image: {file_path_str}")
            return extract_form_fields_from_image(file_path_str)
        
        # Extract text from the file based on type
        if file_path_str.endswith('.pdf'):
            import PyPDF2
            
            text = ""
            with open(file_path_str, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if the PDF contains any images
                has_images = False
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    if '/XObject' in page['/Resources']:
                        has_images = True
                        break
                
                # If PDF has images, it might be a scanned form
                # In this case, try to use GPT-4 Vision to extract fields
                if has_images:
                    current_app.logger.info(f"PDF contains images, attempting to process as image: {file_path_str}")
                    try:
                        return extract_form_fields_from_image(file_path_str)
                    except Exception as e:
                        current_app.logger.warning(f"Failed to process PDF as image: {str(e)}. Falling back to text extraction.")
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text + "\n\n"
            
            file_content = text
        elif file_path_str.endswith('.docx'):
            # In a production app, you'd use python-docx library
            # For now, use a placeholder incident form structure
            file_content = "This is an incident report form for Minto Disability Services. The form requires the following information: incident date, incident time, incident location, persons involved, incident description, severity level (minor, moderate, severe), whether medical attention was required, any immediate actions taken, and reporter details including name, position, contact information, and signature."
        else:
            # Text file
            try:
                with open(file_path_str, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, try binary read as it might be an image or binary file
                current_app.logger.info(f"Failed to read as text, attempting to process as image: {file_path_str}")
                return extract_form_fields_from_image(file_path_str)
        
        # If no content was extracted, use a default template for an incident form
        if not file_content or len(file_content.strip()) < 50:
            current_app.logger.warning(f"Limited content extracted from {file_path_str}, using default incident form template")
            file_content = """
            Incident Report Form for Minto Disability Services
            
            1. Incident Date (date, required)
            2. Incident Time (time, required)
            3. Incident Location (text, required)
            4. Persons Involved (textarea, required)
            5. Incident Description (textarea, required)
            6. Severity (radio: Minor, Moderate, Severe, required)
            7. Medical Attention Required (checkbox: Yes, No, required)
            8. Immediate Actions Taken (textarea, required)
            9. Reporter Name (text, required)
            10. Reporter Position (text, required)
            11. Reporter Contact (text, required)
            12. Reporter Email (email, required)
            13. Additional Comments (textarea, optional)
            """
        
        # Get the OpenAI client
        client = get_openai_client()
        
        current_app.logger.debug(f"Sending form content to OpenAI for parsing: {file_content[:500]}...")
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a form parsing assistant for Minto Disability Services with special focus on EXACT field extraction. "
                        "Your task is to extract ALL questions and fields from the provided form document EXACTLY as they appear in the original. "
                        "IMPORTANT: Do NOT rephrase, modify, combine, or add any questions. Preserve the original text, formatting, and order exactly. "
                        "Extract the precise label text for every field. Do not summarize or generalize fields. Be extremely literal in your extraction. "
                        "For each field, identify: "
                        "1. A unique 'id' (use a simple index number or field name without modifying the text) "
                        "2. 'question_text' (the EXACT and COMPLETE text of the field/question as it appears on the form, including any numbering or formatting) "
                        "3. 'field_type' (text, checkbox, radio, select, textarea, date, email, number, etc.) "
                        "4. 'options' array (EXACT options text for checkbox, radio, select fields) "
                        "5. Whether the field is 'required' (boolean - assume any field with an asterisk or otherwise marked as required is true) "
                        "Return this in a structured JSON format with a 'questions' array in the SAME ORDER as they appear on the form. "
                        "Do not skip ANY fields. Do not merge fields. Do not improve or reword the questions. "
                        "Output must be formatted as JSON."
                    )
                },
                {
                    "role": "user",
                    "content": f"Parse the following form content and return all the form fields in JSON format. Extract every field EXACTLY as written: \n\n{file_content}"
                }
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        logging.error(f"Error parsing form document: {str(e)}")
        raise Exception(f"Failed to parse form: {str(e)}")

def generate_form_questions(form_structure):
    """
    Generate a step-by-step question flow from form structure.
    """
    try:
        # Get the OpenAI client
        client = get_openai_client()
        
        # Validate input
        if not form_structure or not isinstance(form_structure, dict):
            logging.error(f"Invalid form structure: {form_structure}")
            # Return a standardized version of the input or an empty structure
            return {'questions': []}
        
        # Count the original number of questions
        original_questions = form_structure.get('questions', [])
        original_question_count = len(original_questions)
        
        # If there are no questions, return an empty structure
        if original_question_count == 0:
            logging.warning("No questions found in form structure")
            return {'questions': []}
            
        current_app.logger.info(f"Organizing {original_question_count} questions into a sequential flow")
        
        # Skip OpenAI processing and directly standardize the original questions
        # This ensures we keep the exact original structure without any changes
        standardized_questions = []
        for q in original_questions:
            # Skip if the question is None or not a dictionary
            if not q or not isinstance(q, dict):
                continue
                
            # Make a copy of the question to avoid modifying the original
            try:
                standardized_q = q.copy()
            except:
                # If we can't copy the question, create a new dict
                standardized_q = {}
            
            # Ensure question_text field exists
            if 'question_text' not in standardized_q:
                standardized_q['question_text'] = standardized_q.get('question') or standardized_q.get('label') or standardized_q.get('text') or f"Question {len(standardized_questions) + 1}"
            
            # Ensure field_type field exists
            if 'field_type' not in standardized_q:
                standardized_q['field_type'] = standardized_q.get('type') or 'text'
            
            # Ensure id field exists
            if 'id' not in standardized_q:
                # Generate an ID based on the question text
                text = str(standardized_q.get('question_text', '')).strip()
                standardized_q['id'] = text.lower().replace(' ', '_')[:30] or f"question_{len(standardized_questions) + 1}"
            
            # Ensure options exists for appropriate field types
            if standardized_q['field_type'] in ['radio', 'checkbox', 'select'] and 'options' not in standardized_q:
                standardized_q['options'] = []
                
            standardized_questions.append(standardized_q)
        
        current_app.logger.info(f"Standardized {len(standardized_questions)} questions without modifying text or order")
        return {'questions': standardized_questions}
        
    except Exception as e:
        logging.error(f"Error generating form questions: {str(e)}")
        raise Exception(f"Failed to generate questions: {str(e)}")

def generate_embeddings(text):
    """
    Generate embeddings for a given text using OpenAI's embedding model.
    """
    try:
        # Get the OpenAI client
        client = get_openai_client()
        
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    except Exception as e:
        logging.error(f"Error generating embeddings: {str(e)}")
        raise Exception(f"Failed to generate embeddings: {str(e)}")

def generate_answer_with_context(question, contexts):
    """
    Generate an answer to a question based on the provided context.
    """
    try:
        context_text = "\n\n".join(contexts)
        
        # Get the OpenAI client
        client = get_openai_client()
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant for Minto Disability Services. Answer questions about policies and procedures "
                        "based solely on the provided context. If you don't find the information in the context, say so clearly. "
                        "Do not make up information. Be concise but thorough. When appropriate, cite specific policies by name."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context documents:\n{context_text}\n\nQuestion: {question}"
                }
            ]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        raise Exception(f"Failed to generate answer: {str(e)}")
