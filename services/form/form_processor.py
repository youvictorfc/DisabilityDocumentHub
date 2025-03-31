import os
import uuid
import logging
from typing import List, Dict, Any
import PyPDF2
import json
from datetime import datetime
from flask import current_app
from openai import OpenAI

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
        try:
            # Note: We'll use direct OpenAI processing for docx files
            # as python-docx may have compatibility issues
            return self._extract_from_image(file_path)
        except Exception as e:
            current_app.logger.error(f"Error extracting text from DOCX: {str(e)}")
            return self._extract_from_image(file_path)
    
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
        
        # Prompt engineering for question extraction
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
    
    def validate_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the extracted questions for completeness and consistency."""
        current_app.logger.info(f"Validating {len(questions)} extracted questions")
        
        # Prepare question list for validation
        question_texts = "\n".join([f"{i+1}. {q.get('question', 'Unknown question')}" for i, q in enumerate(questions)])
        
        prompt = f"""
        Review these {len(questions)} questions extracted from a form and identify any issues:
        
        {question_texts}
        
        Issues to look for:
        1. Missing questions (check for numerical sequences, lettered items, or logical gaps)
        2. Incomplete questions (missing parts or context)
        3. Questions that should be split into multiple questions
        4. Questions that are not questions (instructions, headers, etc.)
        
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
                        "content": "You are a form validation system. Your task is to ensure that all questions from a form have been correctly extracted."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            validation_result = json.loads(response.choices[0].message.content)
            
            # Log validation issues
            is_complete = validation_result.get("complete", True)
            issues = validation_result.get("issues", [])
            
            if not is_complete:
                current_app.logger.warning("Question extraction may be incomplete")
                for issue in issues:
                    current_app.logger.warning(f"Validation issue: {issue}")
            else:
                current_app.logger.info("Question extraction validation passed")
                
            return validation_result
                
        except Exception as e:
            current_app.logger.error(f"Error validating questions: {str(e)}")
            # Return a default validation result in case of error
            return {
                "complete": True,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": [],
                "missed_questions": []
            }
    
    def process_form(self, file_path: str, form_name: str, description: str = "") -> Dict[str, Any]:
        """Process a form file and return structured form data."""
        current_app.logger.info(f"Processing form: {form_name} from {file_path}")
        
        try:
            # 1. Extract text from document
            document_text = self.extract_text_from_document(file_path)
            
            # 2. Extract questions from text
            initial_questions = self.extract_questions(document_text)
            current_app.logger.info(f"Initial parsing found {len(initial_questions)} questions/fields")
            
            # 3. Validate questions for completeness
            validation_result = self.validate_questions(initial_questions)
            
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