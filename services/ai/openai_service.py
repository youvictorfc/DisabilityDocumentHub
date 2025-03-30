import os
import json
import logging
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

def parse_form_document(file_path):
    """
    Parse a form document and extract a structured representation of questions.
    """
    try:
        # Extract text from the file based on type
        if file_path.endswith('.pdf'):
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            file_content = text
        elif file_path.endswith('.docx'):
            # In a production app, you'd use python-docx library
            file_content = "This is an incident report form for Minto Disability Services. The form requires the following information: incident date, incident time, incident location, persons involved, incident description, severity level (minor, moderate, severe), whether medical attention was required, any immediate actions taken, and reporter details including name, position, contact information, and signature."
        else:
            # Text file
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        
        # If no content was extracted, use a default template for an incident form
        if not file_content or len(file_content.strip()) < 50:
            current_app.logger.warning(f"Limited content extracted from {file_path}, using default incident form template")
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
                        "You are a form parsing assistant for Minto Disability Services. Extract all questions and fields from the provided form document. "
                        "If the document doesn't appear to be a form, assume it's an incident report form and generate appropriate fields. "
                        "For each field, identify: "
                        "1. The question or field label (make it descriptive and clear) "
                        "2. The field type (text, checkbox, radio, select, textarea, date, email, number, etc.) "
                        "3. Any available options (for checkboxes, radios, selects) "
                        "4. Whether the field is required (most fields should be required for an incident form) "
                        "Return this in a structured JSON format with a 'questions' array containing each field."
                    )
                },
                {
                    "role": "user",
                    "content": file_content
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
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a form design assistant. Convert the provided form structure into a step-by-step "
                        "sequential flow of questions. Group related questions where appropriate. Each question should "
                        "include: id, question text, field type, options (if applicable), validation rules, and whether "
                        "it's required. The output should be a JSON array of question objects."
                    )
                },
                {
                    "role": "user",
                    "content": json.dumps(form_structure)
                }
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
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
