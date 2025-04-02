import os
import uuid
import logging
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
        
        # Standard question extraction for regular forms
        prompt = f"""
        Extract ALL questions from this form document. Do not miss any questions, including sub-questions.
        
        Include:
        1. The EXACT question text as it appears in the document, preserving capitalization and punctuation
        2. The question type (text, textarea, radio, checkbox, select, date, email, number, etc.)
        3. Any options for multiple choice questions
        4. Whether the question is required
        
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
        
        IMPORTANT:
        - DO NOT miss any questions, even if they seem minor
        - DO NOT modify the question text in any way - use the EXACT original wording
        - DO NOT combine questions - each question should be a separate entry
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
                        "content": "You are a form processing system. Your task is to extract ALL questions from forms with 100% accuracy. Do not miss any questions. Do not modify the text of questions."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                extracted_data = json.loads(response.choices[0].message.content)
                questions = extracted_data.get("questions", [])
                current_app.logger.info(f"Successfully extracted {len(questions)} questions")
                return questions
            except json.JSONDecodeError as e:
                current_app.logger.error(f"JSON decode error: {str(e)}")
                current_app.logger.error(f"Raw response: {response.choices[0].message.content}")
                return []
                
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
                        "content": (
                            "You are a specialized form field extractor. Your job is to identify ALL input areas "
                            "in structured forms, even when they don't appear as traditional questions. Look for "
                            "labels, blank spaces, underlines, checkboxes, and any other indicators that user input "
                            "is expected. Incident forms, medical forms, and administrative forms often use these patterns."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                extracted_data = json.loads(response.choices[0].message.content)
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
        Review these {len(questions)} questions extracted from a form and identify any issues:
        
        EXTRACTED QUESTIONS:
        {question_texts}
        
        {context_section}
        
        VALIDATION TASKS:
        1. Check for missing questions (look for numerical sequences, lettered items, or logical gaps)
        2. Identify incomplete questions (missing parts or context)
        3. Find questions that should be split into multiple questions
        4. Look for questions that are not questions (instructions, headers, etc.)
        5. Compare with the original document text (if provided) to spot missed fields
        6. Verify if any fields are mentioned in the text but not in the extracted questions
        7. Check for form elements like checkboxes, signature lines, or date fields that may have been missed
        
        Format your response as a JSON object with:
        {{
            "complete": true|false (whether the extraction seems complete),
            "issues": ["issue 1", "issue 2", ...],
            "suggestions": ["suggestion 1", "suggestion 2", ...],
            "missed_questions": ["missed question 1", "missed question 2", ...]
        }}
        """
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a specialized form validation expert. Your task is to analyze extracted form 
                        questions for completeness, accuracy and thoroughness. You have exceptional attention to detail
                        and can identify subtle patterns that might indicate missing questions. You are particularly 
                        attentive to number sequences, section headings, and standard form components like signature 
                        fields that might be missed in extraction."""
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
            
            # Extract original text for completeness
            try:
                document_text = self.extract_text_from_document(file_path)
            except Exception as e:
                current_app.logger.warning(f"Could not extract original text from Access Audit Checklist: {str(e)}")
                document_text = "Access Audit Checklist - Unable to extract full original text"
                
            # Create the form structure with the specialized template
            form_structure = {
                "title": form_name,
                "description": description or "Access Audit Checklist",
                "questions": questions,
                "original_text": document_text
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
            
            # Extract original text for completeness
            try:
                document_text = self.extract_text_from_document(file_path)
            except Exception as e:
                current_app.logger.warning(f"Could not extract original text from Act as an Advocate Form: {str(e)}")
                document_text = "Act as an Advocate Form - Unable to extract full original text"
                
            # Create the form structure with the specialized template
            form_structure = {
                "title": form_name,
                "description": description or "Act as an Advocate Form",
                "questions": questions,
                "original_text": document_text
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
                
                # Use the already extracted document text for the incident form
                # Create the form structure with the specialized template
                form_structure = {
                    "title": form_name,
                    "description": description or "Incident Form",
                    "questions": questions,
                    "original_text": document_text
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
            
            # 5. Create form structure with original text
            form_structure = {
                "questions": processed_questions,
                "original_text": document_text  # Include the full original text
            }
            
            current_app.logger.info(f"Final structured form has {len(processed_questions)} questions and {len(document_text)} characters of original text")
            
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