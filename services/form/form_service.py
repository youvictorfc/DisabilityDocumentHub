import json
import logging
import os
from datetime import datetime
from flask import current_app
from services.ai.openai_service import parse_form_document, generate_form_questions
from services.form.form_processor import FormProcessor

def get_form_processor():
    """Get or create a FormProcessor instance."""
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    return FormProcessor(openai_api_key)

def extract_form_structure(file_path):
    """
    Extract form structure from a document file.
    This is a multi-step process:
    1. Parse the raw form document to identify all fields EXACTLY as they appear in the original
    2. Structure into a step-by-step flow while preserving the EXACT original text and order
    
    CRITICAL: Questions must remain exactly as they appear in the uploaded form - same wording, format and order.
    No form questions should be changed, reworded, improved, or reordered during processing.
    """
    try:
        # Log the start of form extraction
        current_app.logger.info(f"Starting EXACT form extraction for file: {file_path}")
        
        # Use the enhanced FormProcessor for better extraction
        form_processor = get_form_processor()
        form_name = os.path.basename(file_path)
        
        # Process the form using our enhanced processor
        current_app.logger.info(f"Processing form document using enhanced FormProcessor: {file_path}")
        form_data = form_processor.process_form(file_path, form_name)
        
        # Extract the form structure
        form_structure = form_data.get('structure')
        
        # Get validation results
        validation = form_data.get('validation', {})
        is_complete = validation.get('complete', True)
        
        # Log validation issues
        if not is_complete:
            issues = validation.get('issues', [])
            current_app.logger.warning("Form validation identified potential issues:")
            for issue in issues:
                current_app.logger.warning(f" - {issue}")
                
            missed_questions = validation.get('missed_questions', [])
            if missed_questions:
                current_app.logger.warning("Potentially missed questions:")
                for missed in missed_questions:
                    current_app.logger.warning(f" - {missed}")
        
        # Check if any questions were found
        questions = form_structure.get('questions', [])
        questions_count = len(questions)
        
        if questions_count == 0:
            current_app.logger.error("No questions were extracted from the form. Using a fallback form template.")
            # Create a simple fallback form if no questions were found
            form_structure = {
                "questions": [
                    {
                        "id": "form_name",
                        "question_text": "Form Name",
                        "field_type": "text",
                        "required": True
                    },
                    {
                        "id": "form_description",
                        "question_text": "Form Description",
                        "field_type": "textarea",
                        "required": True
                    }
                ]
            }
            
        return form_structure
    
    except Exception as e:
        logging.error(f"Error extracting form structure: {str(e)}")
        raise Exception(f"Failed to extract form structure: {str(e)}")

def validate_form_submission(form_structure, answers):
    """
    Validate that all required fields have been completed.
    """
    questions = form_structure.get('questions', [])
    missing_fields = []
    
    for question in questions:
        question_id = question.get('id')
        # Handle different field name variations in the structure
        is_required = question.get('required', False)
        # Get the question text from various possible field names
        question_text = question.get('question_text') or question.get('question') or question.get('label') or f"Question {question_id}"
        
        if is_required and (question_id not in answers or not answers[question_id]):
            missing_fields.append({
                'id': question_id,
                'question': question_text
            })
    
    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields
    }

def get_next_question(form_structure, current_question_id, answers):
    """
    Determine the next question to display based on current answers.
    Allows for conditional logic in forms.
    """
    questions = form_structure.get('questions', [])
    
    # If there's no current question, return the first one
    if not current_question_id:
        return questions[0] if questions else None
    
    # Find the current question's index
    current_index = next((i for i, q in enumerate(questions) if q.get('id') == current_question_id), -1)
    
    if current_index == -1 or current_index >= len(questions) - 1:
        return None  # No more questions
    
    next_question = questions[current_index + 1]
    
    # Check if there's conditional logic to skip questions
    # This is a simple implementation - could be expanded for more complex logic
    condition = next_question.get('condition')
    if condition:
        condition_field = condition.get('field')
        condition_value = condition.get('value')
        condition_operator = condition.get('operator', 'equals')
        
        if condition_field in answers:
            user_value = answers[condition_field]
            
            if condition_operator == 'equals' and user_value != condition_value:
                # Skip this question and get the next one
                return get_next_question(form_structure, next_question.get('id'), answers)
            elif condition_operator == 'not_equals' and user_value == condition_value:
                # Skip this question and get the next one
                return get_next_question(form_structure, next_question.get('id'), answers)
    
    return next_question
