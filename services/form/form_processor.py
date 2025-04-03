import os
import uuid
import logging
# Import jsonschema if available, but don't require it
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Define our own ValidationError class
class ValidationError(Exception):
    """Custom validation error class for schema validation"""
    pass
from typing import List, Dict, Any
import PyPDF2
import json
from datetime import datetime
from flask import current_app
from openai import OpenAI

# Import our specialized templates for different form types
from services.form.incident_form_template import get_incident_form_template, is_incident_form
from services.form.audit_checklist_template import get_access_audit_checklist_template, is_access_audit_checklist
from services.form.advocate_form_template import get_advocate_form_template, is_advocate_form

# JSON Schema for question validation
FORM_QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["question"],
                "properties": {
                    "question": {"type": "string"},
                    "type": {
                        "type": "string", 
                        "enum": ["text", "textarea", "radio", "checkbox", "select", "date", "email", 
                                "number", "phone", "time", "datetime", "signature"]
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "required": {"type": "boolean"}
                }
            }
        }
    },
    "required": ["questions"]
}

# JSON Schema for validation result
VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "complete": {"type": "boolean"},
        "issues": {
            "type": "array",
            "items": {"type": "string"}
        },
        "suggestions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "missed_questions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["complete"]
}

def validate_json_schema(data, schema):
    """Validate JSON data against a schema"""
    # Basic validation that works regardless of jsonschema availability
    if not isinstance(data, dict):
        return False, "Data is not a dictionary"
    
    # For questions schema, do basic checks
    if schema == FORM_QUESTION_SCHEMA:
        if "questions" not in data:
            return False, "Missing 'questions' key in data"
        if not isinstance(data["questions"], list):
            return False, "Questions must be a list"
        
        # Check each question has required fields
        for q in data["questions"]:
            if not isinstance(q, dict):
                return False, "Question entry must be a dictionary"
            if "question" not in q:
                return False, "Missing 'question' field in question entry"
        
        return True, None
        
    # For validation schema, do basic checks    
    elif schema == VALIDATION_SCHEMA:
        if "complete" not in data:
            return False, "Missing 'complete' field in validation data"
        return True, None
    
    # If jsonschema is available, do more thorough validation
    if 'jsonschema' in globals() and HAS_JSONSCHEMA:
        module = globals()['jsonschema']
        try:
            module.validate(instance=data, schema=schema)
            return True, None
        except Exception as e:
            return False, f"Schema validation error: {str(e)}"
    
    # If we reached here, basic validation passed
    return True, None

class FormProcessor:
    """Service for processing forms, extracting questions, and managing form structure."""
    
    def __init__(self, openai_api_key=None):
        """Initialize the FormProcessor with OpenAI API key."""
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        
    def extract_text_from_document(self, file_path: str) -> str:
        """Extract text content from a document (PDF, DOCX, or image)."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            return self._extract_from_image(file_path)
        elif file_extension == '.txt':
            return self._extract_from_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        current_app.logger.info(f"Extracting text from PDF file: {file_path}")
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            current_app.logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            current_app.logger.error(f"Error extracting text from PDF: {str(e)}")
            # Use OpenAI as a fallback for problematic PDFs
            return self._extract_from_image(file_path)
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        current_app.logger.info(f"Extracting text from DOCX file: {file_path}")
        
        # First, try to use python-docx if it's available
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
            # If successful and we got some content, return it
            if text and len(text) > 100:  # Arbitrary minimum content check
                current_app.logger.info(f"Successfully extracted {len(text)} characters from DOCX using python-docx")
                return text
        except Exception as docx_error:
            current_app.logger.warning(f"Could not extract text using python-docx: {str(docx_error)}")
        
        # As a second try, attempt to extract text as a Word document (binary)
        try:
            # Try to read directly from file as text
            with open(file_path, 'rb') as file:
                file_content = file.read()
                
            # Create a specialized prompt for form extraction
            import base64
            base64_encoded = base64.b64encode(file_content).decode("utf-8")
            
            # Use the vision model but with specialized form extraction instructions
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a specialized form extraction system designed to identify form questions and fields. When given a form document, extract ALL questions, fields, labels, and input areas. Pay special attention to form structure, including checkboxes, blank lines for text input, and section headers."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": (
                                    "Extract ALL form questions and fields from this document. "
                                    "For form extraction, please:\n"
                                    "1. Identify every question, prompt, or label, even those without question marks\n"
                                    "2. Include blank lines, checkboxes, radio buttons as they indicate input fields\n"
                                    "3. Note section titles and organizational elements\n"
                                    "4. Preserve the exact original text and format\n"
                                    "5. Include all date fields, name fields, signature fields, etc.\n\n"
                                    "If a line has a colon or ends with blank space for writing, it's likely a form field."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64_encoded}"}
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )
            
            extracted_text = response.choices[0].message.content
            current_app.logger.info(f"Successfully extracted {len(extracted_text)} characters from DOCX using OpenAI")
            return extracted_text
            
        except Exception as e:
            current_app.logger.error(f"Error extracting text from DOCX using specialized approach: {str(e)}")
            
            # Last resort - try the generic image-based extraction
            try:
                return self._extract_from_image(file_path)
            except Exception as image_error:
                current_app.logger.error(f"DOCX extraction completely failed: {str(image_error)}")
                raise ValueError(f"Could not extract content from this DOCX file: {str(image_error)}")
    
    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file."""
        current_app.logger.info(f"Extracting text from text file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_from_image(self, file_path: str) -> str:
        """
        Extract text from an image or document using OpenAI's multimodal capabilities.
        This also serves as a fallback for PDFs and DOCXs that can't be parsed natively.
        """
        current_app.logger.info(f"Using OpenAI to extract text from file: {file_path}")
        
        # Check if this is actually a supported image/document format
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Determine the correct MIME type based on file extension
        mime_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
        }
        
        mime_type = mime_type_map.get(file_extension, 'application/octet-stream')
        
        # Explicitly check if this is a supported format for OpenAI's image API
        supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        # If it's not a supported image format, try to extract text using a different method
        if file_extension not in supported_image_formats and file_extension != '.pdf':
            if file_extension == '.txt':
                # For text files, use the text extractor
                return self._extract_from_text(file_path)
            else:
                # For other unsupported formats, convert text extraction to a text-only prompt
                current_app.logger.warning(f"File format {file_extension} is not directly supported for image processing.")
                current_app.logger.info("Attempting to extract content as text...")
                
                # Try to read as text with various encodings
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            file_content = f.read()
                    except Exception:
                        raise ValueError(f"Cannot process this file format: {file_extension}. Please convert it to a supported format (PDF, JPG, PNG, etc.)")
                
                # Process the text content with OpenAI
                prompt = f"""
                The following content is from a form document. Extract all form questions, options, and structure:
                
                {file_content[:8000]}  # Limit content length to avoid token limits
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a document processing assistant. Extract ALL text content, especially form questions and fields."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000
                )
                
                extracted_text = response.choices[0].message.content
                current_app.logger.info(f"Successfully extracted {len(extracted_text)} characters from text content")
                return extracted_text
        
        try:
            import base64
            import mimetypes
            
            # Read and encode the file
            with open(file_path, "rb") as file:
                file_content = file.read()
                base64_encoded = base64.b64encode(file_content).decode("utf-8")
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a document processing assistant that extracts text from images and documents. Extract ALL text from the provided document with high accuracy."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Extract ALL text from this document. Include all questions, text, headers, footers, and form fields. Preserve the original formatting and structure as much as possible."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{base64_encoded}"}
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )
            
            extracted_text = response.choices[0].message.content
            current_app.logger.info(f"Successfully extracted {len(extracted_text)} characters using OpenAI")
            return extracted_text
            
        except Exception as e:
            current_app.logger.error(f"Error using OpenAI for text extraction: {str(e)}")
            
            # Provide more helpful error message based on the exception
            if "unsupported image" in str(e).lower():
                raise ValueError(f"Unsupported file format: {file_extension}. Please use one of these formats: PDF, PNG, JPEG, GIF, or WebP.")
            elif "too large" in str(e).lower():
                raise ValueError("The file is too large for processing. Please reduce the file size or split it into smaller documents.")
            else:
                raise ValueError(f"Failed to extract text from the document: {str(e)}")
    
    def extract_questions(self, document_text: str) -> List[Dict[str, Any]]:
        """Extract all questions from the document text using OpenAI."""
        current_app.logger.info("Extracting questions from document text")
        
        # Check if this looks like a form with few or no question marks (like an incident form)
        question_mark_count = document_text.count('?')
        line_count = document_text.count('\n')
        
        # If few question marks but many lines, it might be a form with implicit questions
        if question_mark_count < 5 and line_count > 20:
            current_app.logger.info(f"Detected potential form with few explicit questions ({question_mark_count} question marks, {line_count} lines)")
            return self._extract_form_fields(document_text)
        
        # Standard question extraction for regular forms with enhanced instructions
        prompt = f"""
        You are a specialized form analyzer with the critical task of extracting EVERY SINGLE question, field, and input area from the provided form document.
        Your extraction must be 100% COMPLETE and EXACT. Missing even one field is considered a critical failure.
        
        EXTRACTION REQUIREMENTS:
        1. Extract ALL questions, fields, and input areas in the EXACT order they appear in the document
        2. Preserve the EXACT original text, including:
           - All capitalization, punctuation, and formatting
           - All numbering or lettering systems (e.g., "1.", "a)", "i.")
           - Any instructions or context preceding or following questions
        3. Identify the appropriate field type for each question:
           - text: for short single-line answers
           - textarea: for longer, multi-line responses
           - radio: for single-selection options (Yes/No, multiple choice)
           - checkbox: for multiple-selection options
           - select: for dropdown selections
           - date: for date inputs
           - email: for email addresses
           - number: for numerical inputs
           - phone: for phone numbers
           - time: for time inputs
        4. For checkbox, radio and select types, include ALL options exactly as written
        5. Determine whether each field is required based on context
        
        CRITICAL EXTRACTION APPROACH:
        - Carefully examine the ENTIRE document for ALL possible input fields
        - Look for lines that end with colons, blank spaces, underscores or boxes
        - Identify any tables with rows that need responses
        - Check for signature and date fields at the end of the form
        - Pay special attention to YES/NO questions, checkboxes, and option lists
        - Consider section headings and instructions that may introduce fields
        - Look for any numbered or lettered items that may require responses
        
        Format the output as a JSON array of questions with this structure:
        {{
            "questions": [
                {{
                    "question": "The exact question text",
                    "type": "text|textarea|radio|checkbox|select|date|email|number",
                    "options": ["Option 1", "Option 2"] (only for radio, checkbox, select types),
                    "required": true|false
                }}
            ]
        }}
        
        ABSOLUTE REQUIREMENTS:
        - DO NOT miss ANY questions, fields, or input areas, no matter how small or seemingly insignificant
        - DO NOT modify the question text in ANY way - use the EXACT original wording
        - DO NOT combine or merge questions - each question must be a separate entry
        - DO NOT reorder questions - maintain the EXACT order from the document
        - DO NOT omit context or instructions that help understand the question
        - DO NOT add or modify numbering or lettering that isn't in the original
        - For forms with checkboxes or multiple selections, include all options
        - Identify instruction text preceding or around questions, and include it in the question text
        - Look for blank lines, text followed by colons, and other patterns that indicate form fields
        - Treat all blank spaces for writing as text input fields
        
        Document text:
        {document_text}
        """
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an advanced form processing system with perfect attention to detail. Your task is to extract ALL questions and fields from forms with 100% accuracy and completeness.

EXTRACTION PRINCIPLES:
1. Thoroughness: You must identify and extract EVERY question and field, no matter how minor
2. Exactness: Preserve the EXACT text, capitalization, punctuation, and formatting
3. Ordering: Maintain the EXACT order of questions as they appear in the document
4. Integrity: Never combine, split, rephrase or modify questions in any way
5. Comprehensiveness: Include all context and instructions surrounding questions

Forms often contain various input mechanisms beyond just explicit questions, you must identify:
- Standard questions with question marks
- Implicitly required information (Name:, Address:, etc.)
- Blank lines or spaces for writing
- Checkboxes and radio buttons
- Signature fields and date fields
- Tables with input cells
- Any text that implies the need for user input"""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                extracted_data = json.loads(response.choices[0].message.content)
                
                # Validate extracted data against our JSON schema
                is_valid, error = validate_json_schema(extracted_data, FORM_QUESTION_SCHEMA)
                
                if not is_valid:
                    current_app.logger.warning(f"Extracted questions failed schema validation: {error}")
                    current_app.logger.warning("Will attempt to correct the structure...")
                    
                    # If schema validation failed but we have some data, try to fix it
                    if isinstance(extracted_data, dict) and ("questions" in extracted_data or "fields" in extracted_data):
                        # Check for alternative keys that might have been used
                        questions = extracted_data.get("questions", extracted_data.get("fields", []))
                        
                        # Ensure every question has the required fields
                        for q in questions:
                            if "question" not in q and "text" in q:
                                q["question"] = q["text"]
                            if "type" not in q:
                                q["type"] = "text"
                            if "required" not in q:
                                q["required"] = False
                        
                        corrected_data = {"questions": questions}
                        # Validate the corrected data
                        is_valid, _ = validate_json_schema(corrected_data, FORM_QUESTION_SCHEMA)
                        
                        if is_valid:
                            current_app.logger.info("Successfully corrected the questions structure")
                            questions = corrected_data["questions"]
                            current_app.logger.info(f"Successfully extracted {len(questions)} questions")
                            return questions
                    
                    # If correction attempt failed, log and proceed to fallback
                    current_app.logger.error("Could not correct schema validation issues, trying fallback extraction")
                    return self._fallback_form_extraction(document_text)
                
                # If schema validation passed, extract questions normally
                questions = extracted_data.get("questions", [])
                current_app.logger.info(f"Successfully extracted {len(questions)} questions")
                return questions
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"JSON decode error: {str(e)}")
                current_app.logger.error(f"Raw response: {response.choices[0].message.content}")
                # Try fallback extraction on JSON parse failure
                return self._fallback_form_extraction(document_text)
                
        except Exception as e:
            current_app.logger.error(f"Error extracting questions: {str(e)}")
            raise ValueError(f"Failed to extract questions: {str(e)}")
    
    def _extract_form_fields(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Extract form fields from documents that may not have explicit questions.
        This is particularly useful for forms like incident reports where fields
        are often indicated by blank spaces or colons rather than question marks.
        """
        current_app.logger.info("Using specialized form field extraction for structured forms")
        
        # Special handling for incident forms
        if is_incident_form(document_text):
            current_app.logger.info("Detected an incident form! Using predefined template.")
            return get_incident_form_template()
        
        # Special prompt engineering for structured forms
        prompt = f"""
        This is a specialized form with fields that need extraction. It may not have explicit questions, 
        but instead has labeled fields, spaces for input, checkboxes, etc. Extract ALL form fields.
        
        For each field, identify:
        1. The field label or prompt (EXACTLY as written)
        2. The field type (text, textarea, radio, checkbox, select, date, signature, etc.)
        3. Any options for selection fields
        4. Whether the field is required (assume required if it's a core part of the form)
        
        Treat as fields:
        - Lines ending with a colon (:)
        - Lines followed by blank space for writing
        - Blank spaces with underscores or lines for input
        - Checkbox or radio button options
        - Date fields
        - Signature fields
        - Any other elements that request user input
        
        Format as a JSON array of fields with this structure:
        {{
            "questions": [
                {{
                    "question": "The exact field label/prompt",
                    "type": "text|textarea|radio|checkbox|select|date|signature",
                    "options": ["Option 1", "Option 2"] (for radio, checkbox, select types),
                    "required": true|false
                }}
            ]
        }}
        
        CRITICAL GUIDELINES:
        - DO NOT miss any fields or input areas
        - Preserve the EXACT label text, don't rephrase or combine fields
        - Include ALL fields: name fields, dates, incidents, locations, signatures, etc.
        - For unlabeled input areas, use the closest heading or context as the label
        - Convert each section that requires input into a proper form field
        
        Document text:
        {document_text}
        """
        
        try:
            # Use GPT-4 with specialized form extraction prompt
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert form field extractor specialized in extracting input fields from complex, highly structured forms where fields might not appear as traditional questions.

EXTRACTION GOALS:
1. Identify and extract EVERY possible input field, regardless of how it's presented
2. Maintain the EXACT wording of each field label without modifications
3. Preserve the EXACT order of fields as they appear in the document
4. Determine the most appropriate field type for each input area
5. Identify all options for multiple-choice or selection fields

FORM FIELD PATTERNS TO IDENTIFY:
- Standard questions with question marks
- Lines ending with colons followed by blank space
- Underlined spaces, boxes, or blank areas for writing
- Checkboxes and radio buttons with their corresponding options
- Tables with cells that need to be filled
- Signature spaces and date fields
- Numbered or bulleted items requiring responses
- Yes/No choices and other option pairs
- Instructions that imply user input is required
- Fields for personal information (name, address, contact details)

You must be extremely thorough in your extraction, treating ANY text that could require user input as a form field that must be included."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                extracted_data = json.loads(response.choices[0].message.content)
                
                # Validate extracted data against our JSON schema
                is_valid, error = validate_json_schema(extracted_data, FORM_QUESTION_SCHEMA)
                
                if not is_valid:
                    current_app.logger.warning(f"Specialized extraction failed schema validation: {error}")
                    current_app.logger.warning("Attempting to correct the structure...")
                    
                    # If schema validation failed but we have some data, try to fix it
                    if isinstance(extracted_data, dict) and ("questions" in extracted_data or "fields" in extracted_data):
                        # Check for alternative keys that might have been used
                        questions = extracted_data.get("questions", extracted_data.get("fields", []))
                        
                        # Ensure every question has the required fields
                        for q in questions:
                            if "question" not in q and "text" in q:
                                q["question"] = q["text"]
                            if "type" not in q:
                                q["type"] = "text"
                            if "required" not in q:
                                q["required"] = False
                            if q.get("type") in ["radio", "checkbox", "select"] and "options" not in q:
                                q["options"] = []
                        
                        corrected_data = {"questions": questions}
                        # Validate the corrected data
                        is_valid, _ = validate_json_schema(corrected_data, FORM_QUESTION_SCHEMA)
                        
                        if is_valid:
                            current_app.logger.info("Successfully corrected the specialized extraction structure")
                            questions = corrected_data["questions"]
                            current_app.logger.info(f"Successfully extracted {len(questions)} form fields")
                            return questions
                    
                    # If correction attempt failed, log and proceed to fallback
                    current_app.logger.error("Could not correct schema validation issues, using fallback extraction")
                    return self._fallback_form_extraction(document_text)
                
                # If schema validation passed, extract questions normally
                questions = extracted_data.get("questions", [])
                current_app.logger.info(f"Successfully extracted {len(questions)} form fields using specialized extractor")
                
                # If no questions were found, try one more time with a different approach
                if len(questions) == 0:
                    return self._fallback_form_extraction(document_text)
                    
                return questions
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"JSON decode error in form field extraction: {str(e)}")
                current_app.logger.error(f"Raw response: {response.choices[0].message.content}")
                return self._fallback_form_extraction(document_text)
                
        except Exception as e:
            current_app.logger.error(f"Error extracting form fields: {str(e)}")
            # When all else fails, try to create a basic form structure from the document
            return self._fallback_form_extraction(document_text)
    
    def _fallback_form_extraction(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Last-resort fallback method to extract form fields when other methods fail.
        This method is more aggressive in finding anything that could be a form field.
        """
        current_app.logger.warning("Using fallback form field extraction method")
        
        # Analyze the document lines to identify potential fields
        lines = [line.strip() for line in document_text.split('\n') if line.strip()]
        extracted_fields = []
        
        for i, line in enumerate(lines):
            # Skip very short lines or lines that are likely headers (all caps)
            if len(line) < 3 or (line.upper() == line and len(line) > 5):
                continue
                
            # Lines that end with colon are almost certainly field labels
            if line.endswith(':'):
                field_name = line.rstrip(':').strip()
                extracted_fields.append({
                    "question": field_name,
                    "type": "text",
                    "required": False
                })
                continue
                
            # Lines that contain question-like words
            question_indicators = ['type', 'name', 'date', 'location', 'address', 'description', 
                               'action', 'signed', 'reported', 'witness', 'incident']
            
            if any(indicator in line.lower() for indicator in question_indicators):
                # Check if this line has a form-like structure
                if ':' in line:
                    # Split at the first colon
                    field_name = line.split(':', 1)[0].strip()
                    extracted_fields.append({
                        "question": field_name,
                        "type": "text",
                        "required": False
                    })
                else:
                    # Take the whole line as a potential field
                    extracted_fields.append({
                        "question": line,
                        "type": "text",
                        "required": False
                    })
            
            # Lines that mention checkbox, radio buttons, or selection
            if 'check' in line.lower() or 'circle' in line.lower() or 'select' in line.lower():
                options = []
                
                # Look for options in the next few lines
                for j in range(1, min(5, len(lines) - i)):
                    next_line = lines[i + j].strip()
                    if next_line and len(next_line) < 30 and not next_line.endswith(':'):
                        options.append(next_line)
                
                field_type = "checkbox" if "check" in line.lower() else "radio"
                
                extracted_fields.append({
                    "question": line,
                    "type": field_type,
                    "options": options,
                    "required": False
                })
        
        # If we found fields, return them
        if extracted_fields:
            current_app.logger.info(f"Fallback extraction found {len(extracted_fields)} potential form fields")
            return extracted_fields
            
        # Absolute last resort - create a basic structure based on document sections
        # This ensures we have at least some fields rather than none
        current_app.logger.warning("Using emergency fallback - creating basic fields from document structure")
        
        basic_fields = [
            {"question": "Incident Type", "type": "text", "required": True},
            {"question": "Date and Time", "type": "datetime", "required": True},
            {"question": "Location", "type": "text", "required": True},
            {"question": "Description", "type": "textarea", "required": True},
            {"question": "Actions Taken", "type": "textarea", "required": False},
            {"question": "Reported By", "type": "text", "required": True},
            {"question": "Signature", "type": "text", "required": True}
        ]
        
        return basic_fields
            
    def validate_questions(self, questions: List[Dict[str, Any]], document_text: str = None) -> Dict[str, Any]:
        """
        Validate the extracted questions for completeness and consistency.
        If document_text is provided, perform a deeper verification against the original text.
        """
        current_app.logger.info(f"Validating {len(questions)} extracted questions")
        
        # Prepare question list for validation
        question_key = 'question_text' if any('question_text' in q for q in questions) else 'question'
        question_texts = "\n".join([f"{i+1}. {q.get(question_key, q.get('question', 'Unknown question'))}" for i, q in enumerate(questions)])
        
        # If we have the original document text, we can do a more thorough validation
        context_section = ""
        if document_text and len(document_text) > 0:
            # Limit the document text to prevent token limit issues
            max_context_length = 3000
            if len(document_text) > max_context_length:
                context_section = f"""
                ORIGINAL DOCUMENT TEXT (partial):
                {document_text[:max_context_length]}
                ... [truncated] ...
                """
            else:
                context_section = f"""
                ORIGINAL DOCUMENT TEXT:
                {document_text}
                """
        
        prompt = f"""
        You are a form validation expert conducting a thorough verification of extracted questions to ensure MAXIMUM ACCURACY. 
        Nothing is more important than capturing ALL questions EXACTLY as they appear in the original form.
        
        Review these {len(questions)} questions extracted from a form and identify any issues:
        
        EXTRACTED QUESTIONS:
        {question_texts}
        
        {context_section}
        
        CRITICAL VALIDATION TASKS:
        1. EXACT QUESTION IDENTIFICATION: Look for signs of questions in the original text that were completely missed, such as:
           - Questions with question marks
           - Lines ending with colons
           - Fields with blank spaces for writing
           - Numbered or lettered items that form a sequence
           - Table rows with empty cells to be filled
           - Checkbox items or option lists
           - Signature, date, or approval fields
           - Any text that implies user input is required
        
        2. THOROUGH VERIFICATION: Compare the extracted questions with the original document text, looking carefully for:
           - Questions that appear in the document but not in the extracted list
           - Sections that require input but were not recognized as questions
           - Checkbox options or radio button selections that were missed
           - Form fields indicated by underscores, boxes, or blank spaces
           - Implicit questions (statements expecting a response)
           - Tables or structured content that should be converted to questions
        
        3. FORMAT AND STRUCTURE CHECKS:
           - Are all questions captured exactly as written in the original document?
           - Are question numbers and letters preserved correctly?
           - Are multi-part questions properly identified?
           - Are tables with input fields properly represented?
           - Are dropdown or selection menus captured with all options?
        
        Format your response as a JSON object with:
        {{
            "complete": true|false (whether the extraction seems complete),
            "issues": ["specific issue 1", "specific issue 2", ...],
            "suggestions": ["specific, actionable suggestion 1", "specific, actionable suggestion 2", ...],
            "missed_questions": ["EXACT text of missed question 1", "EXACT text of missed question 2", ...]
        }}
        
        The "missed_questions" field is CRITICALLY IMPORTANT - include the EXACT text of any questions found in the document that were not in the extracted list.
        """
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a highly specialized form validation expert with perfect attention to detail. Your task is to analyze extracted form questions against the original document, identifying ANY discrepancies or missed fields with 100% accuracy.

VALIDATION PRINCIPLES:
1. COMPLETENESS: Your primary goal is to identify ANY questions that exist in the original document but were missed in extraction
2. PRECISENESS: Verify that extracted questions match the EXACT wording, capitalization, and punctuation in the original
3. THOROUGHNESS: Look beyond just obvious questions to identify ALL form fields requiring user input
4. CONTEXT AWARENESS: Consider the document structure, numbering systems, and logical flow

Form fields can appear in many formats beyond just questions with question marks:
- Standard questions with question marks
- Text followed by colons indicating an input field (Name:, Address:)
- Lines or underscores indicating spaces for user input
- Checkboxes and radio button options 
- Tables with cells for user input
- Signature fields, date fields, or initial fields
- Numbered or bulleted lists requiring responses
- Section labels that imply responses (Comments, Feedback, etc.)

Your validation must be exhaustive, identifying ANY field that exists in the original document but was missed in extraction."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2  # Lower temperature for more precise analysis
            )
            
            try:
                validation_result = json.loads(response.choices[0].message.content)
                
                # Log validation issues
                is_complete = validation_result.get('complete', True)
                issues = validation_result.get('issues', [])
                missed_questions = validation_result.get('missed_questions', [])
                
                if not is_complete:
                    current_app.logger.warning("Question extraction may be incomplete")
                    for issue in issues:
                        current_app.logger.warning(f"Validation issue: {issue}")
                    
                    # Log missed questions with more prominent warning
                    if missed_questions:
                        current_app.logger.warning(f"ATTENTION: Validation detected {len(missed_questions)} potentially missed questions")
                        for i, missed in enumerate(missed_questions):
                            current_app.logger.warning(f"Missed question {i+1}: {missed}")
                else:
                    current_app.logger.info("Question extraction validation passed")
                    
                # If we have missed questions, we might want to try to extract them in future improvements
                # This could be implemented here...
                    
                return validation_result
                    
            except json.JSONDecodeError as e:
                current_app.logger.error(f"JSON decode error during validation: {str(e)}")
                current_app.logger.error(f"Raw response: {response.choices[0].message.content}")
                return {
                    "complete": False,
                    "issues": [f"Validation parsing error: {str(e)}"],
                    "suggestions": ["Manual review recommended"],
                    "missed_questions": []
                }
        
        except Exception as e:
            current_app.logger.error(f"Error validating questions: {str(e)}")
            # Return a default validation result in case of error
            return {
                "complete": False,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": ["Manual review recommended due to validation error"],
                "missed_questions": []
            }
    
    def process_form(self, file_path: str, form_name: str, description: str = "") -> Dict[str, Any]:
        """Process a form file and return structured form data."""
        current_app.logger.info(f"Processing form: {form_name} from {file_path}")
        
        # Check for special templates first based on filename
        if is_access_audit_checklist(file_path):
            current_app.logger.info("Detected Access Audit Checklist, using specialized template")
            questions = get_access_audit_checklist_template()
            
            # Create the form structure with the specialized template
            form_structure = {
                "title": form_name,
                "description": description or "Access Audit Checklist",
                "questions": questions
            }
            
            return {
                "structure": form_structure,
                "validation": {
                    "complete": True,
                    "issues": []
                }
            }
            
        if is_advocate_form(file_path):
            current_app.logger.info("Detected Act as an Advocate Form, using specialized template")
            questions = get_advocate_form_template()
            
            # Create the form structure with the specialized template
            form_structure = {
                "title": form_name,
                "description": description or "Act as an Advocate Form",
                "questions": questions
            }
            
            return {
                "structure": form_structure,
                "validation": {
                    "complete": True,
                    "issues": []
                }
            }
        
        try:
            # 1. Extract text from document
            document_text = self.extract_text_from_document(file_path)
            
            # Check if this looks like an incident form based on extracted text
            if is_incident_form(document_text):
                current_app.logger.info("Detected Incident Form pattern, using specialized template")
                questions = get_incident_form_template()
                
                # Create the form structure with the specialized template
                form_structure = {
                    "title": form_name,
                    "description": description or "Incident Form",
                    "questions": questions
                }
                
                return {
                    "structure": form_structure,
                    "validation": {
                        "complete": True,
                        "issues": []
                    }
                }
            
            # 2. Extract questions from text
            initial_questions = self.extract_questions(document_text)
            current_app.logger.info(f"Initial parsing found {len(initial_questions)} questions/fields")
            
            # 3. Validate questions for completeness with original document text for better verification
            validation_result = self.validate_questions(initial_questions, document_text)
            
            # 3.5 Check if validation found missing questions and incorporate them
            missed_questions = validation_result.get('missed_questions', [])
            if missed_questions and len(missed_questions) > 0:
                current_app.logger.info(f"Incorporating {len(missed_questions)} questions detected during validation")
                
                # Add the missed questions to our initial set
                for i, missed_question in enumerate(missed_questions):
                    # Create a basic question structure for each missed question
                    initial_questions.append({
                        "id": f"missed_{i+1}",
                        "question": missed_question,
                        "type": "text",  # Default to text type
                        "required": False  # Default to not required
                    })
                
                current_app.logger.info(f"Updated question count after incorporating missed questions: {len(initial_questions)}")
            
            # 4. Process the questions to ensure all have correct structure
            current_app.logger.info("Processing questions while preserving EXACT text and order...")
            processed_questions = []
            
            for i, question in enumerate(initial_questions):
                # Ensure every question has the required fields
                processed_question = {
                    "id": question.get("id") or f"q_{i+1}",
                    "question_text": question.get("question", ""),
                    "field_type": question.get("type", "text").lower(),
                    "options": question.get("options", []),
                    "required": question.get("required", False)
                }
                
                # Map alternative field type names to standardized types
                field_type_mapping = {
                    "multiple_choice": "radio",
                    "multi_select": "checkbox",
                    "dropdown": "select",
                    "textarea": "textarea",
                    "yes_no": "radio",
                    "yes/no": "radio",
                    "long_text": "textarea",
                    "short_text": "text",
                    "single_line": "text",
                    "multi_line": "textarea",
                    "number": "number",
                    "email": "email",
                    "date": "date",
                    "time": "time",
                    "datetime": "datetime",
                }
                
                # Standardize field types
                if processed_question["field_type"] in field_type_mapping:
                    processed_question["field_type"] = field_type_mapping[processed_question["field_type"]]
                
                # Special case for yes/no questions
                if processed_question["field_type"] == "radio" and (
                    "yes" in processed_question["question_text"].lower() or 
                    "no" in processed_question["question_text"].lower()
                ) and len(processed_question["options"]) == 0:
                    processed_question["options"] = ["Yes", "No"]
                
                # Ensure radio/checkbox/select types have options
                if processed_question["field_type"] in ["radio", "checkbox", "select"] and not processed_question["options"]:
                    # If the field needs options but none were detected, default to appropriate options
                    if "yes" in processed_question["question_text"].lower() or "no" in processed_question["question_text"].lower():
                        processed_question["options"] = ["Yes", "No"]
                    elif any(word in processed_question["question_text"].lower() for word in ["agree", "disagree", "consent", "accept"]):
                        processed_question["options"] = ["Agree", "Disagree"]
                    elif any(word in processed_question["question_text"].lower() for word in ["rate", "scale", "score", "level"]):
                        processed_question["options"] = ["1", "2", "3", "4", "5"]
                
                processed_questions.append(processed_question)
            
            # 5. Create form structure
            form_structure = {
                "questions": processed_questions
            }
            
            current_app.logger.info(f"Final structured form has {len(processed_questions)} questions")
            
            # 6. Create the full form data object
            form_data = {
                "title": form_name,
                "description": description,
                "structure": form_structure,
                "created_at": datetime.now().isoformat(),
                "validation": validation_result
            }
            
            return form_data
            
        except Exception as e:
            current_app.logger.error(f"Error processing form: {str(e)}")
            raise ValueError(f"Failed to process form: {str(e)}")