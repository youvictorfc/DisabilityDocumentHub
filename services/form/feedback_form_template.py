"""
Template-based fallback solution for the Feedback Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any

def get_feedback_form_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Feedback Form 
    with the exact structure matching the document.
    """
    return [
        {
            "id": "section_1",
            "question_text": "Circle the face that matches your thoughts",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_1",
            "question_text": "We do what you want us to do",
            "field_type": "radio",
            "options": ["Happy face", "Neutral face", "Sad face"],
            "required": True
        },
        {
            "id": "question_2",
            "question_text": "We listen to you",
            "field_type": "radio",
            "options": ["Happy face", "Neutral face", "Sad face"],
            "required": True
        },
        {
            "id": "question_3",
            "question_text": "You are making gains towards your goals",
            "field_type": "radio",
            "options": ["Happy face", "Neutral face", "Sad face"],
            "required": True
        },
        {
            "id": "question_4",
            "question_text": "We are clear when we give you information",
            "field_type": "radio",
            "options": ["Happy face", "Neutral face", "Sad face"],
            "required": True
        },
        {
            "id": "question_5",
            "question_text": "You are happy with our service",
            "field_type": "radio",
            "options": ["Happy face", "Neutral face", "Sad face"],
            "required": True
        },
        {
            "id": "section_2",
            "question_text": "Tell us how we are doing!",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_6",
            "question_text": "We like to try and get better and better. Can you tell us how we are doing?",
            "field_type": "readonly",
            "options": [],
            "required": False
        },
        {
            "id": "question_7",
            "question_text": "Feel free to tell us more here:",
            "field_type": "textarea",
            "options": [],
            "required": False
        }
    ]

def is_feedback_form(file_path: str) -> bool:
    """
    Determine if the file is likely a Feedback Form.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be a feedback form
    """
    # Check the filename for a quick identification
    import os
    filename = os.path.basename(file_path).lower()
    
    if "feedback" in filename or "feedback form" in filename:
        return True
    
    # If filename doesn't contain clear indicators, try to detect from content
    if file_path.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        try:
            # Try to extract some text from the file
            from services.document.document_service import extract_text_from_file
            text_content = extract_text_from_file(file_path)
            
            # Check for key phrases that would indicate this is a feedback form
            if text_content:
                indicators = [
                    "circle the face",
                    "tell us how we are doing",
                    "happy with our service",
                    "matches your thoughts"
                ]
                
                text_lower = text_content.lower()
                return any(indicator in text_lower for indicator in indicators)
            
        except Exception as e:
            print(f"Error checking feedback form content: {e}")
            
    return False