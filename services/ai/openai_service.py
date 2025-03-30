import os
import json
import logging
from openai import OpenAI
from flask import current_app

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def parse_form_document(file_path):
    """
    Parse a form document and extract a structured representation of questions.
    """
    try:
        with open(file_path, 'rb') as file:
            # For simplicity, we'll assume we're extracting text content here
            # In a production system, you would use appropriate libraries based on file type
            if file_path.endswith('.pdf'):
                # This is a placeholder - in a real app, you'd use PyPDF2 or similar
                file_content = "Sample PDF content for demonstration"
            elif file_path.endswith('.docx'):
                # This is a placeholder - in a real app, you'd use python-docx
                file_content = "Sample DOCX content for demonstration"
            else:
                # Text file
                file_content = file.read().decode('utf-8')
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a form parsing assistant. Extract all questions and fields from the provided form document. "
                        "Organize them sequentially as they appear in the form. For each field, identify: "
                        "1. The question or field label "
                        "2. The field type (text, checkbox, radio, select, textarea, date, email, number, etc.) "
                        "3. Any available options (for checkboxes, radios, selects) "
                        "4. Whether the field is required "
                        "Return this in a structured JSON format."
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
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
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
        response = openai.embeddings.create(
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
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
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
