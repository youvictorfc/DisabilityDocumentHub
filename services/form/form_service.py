import json
import logging
from services.ai.openai_service import parse_form_document, generate_form_questions

def extract_form_structure(file_path):
    """
    Extract form structure from a document file.
    This is a multi-step process:
    1. Parse the raw form document to identify all fields
    2. Structure the questions into a step-by-step flow
    """
    try:
        # Step 1: Parse the form document to identify fields
        parsed_form = parse_form_document(file_path)
        
        # Step 2: Generate a step-by-step flow of questions
        structured_questions = generate_form_questions(parsed_form)
        
        return structured_questions
    
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
        is_required = question.get('required', False)
        
        if is_required and (question_id not in answers or not answers[question_id]):
            missing_fields.append({
                'id': question_id,
                'question': question.get('question')
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
