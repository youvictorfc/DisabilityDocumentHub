"""
Template-based fallback solution for the Complaints Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any

def get_complaints_form_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Complaints Form 
    with the exact structure matching the document.
    """
    return [
        {
            "id": "section_1",
            "question_text": "Personal Information",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_1",
            "question_text": "Name of Person",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_2",
            "question_text": "Address",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_3",
            "question_text": "Phone",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_4",
            "question_text": "Email",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_5",
            "question_text": "Preferred contact method",
            "field_type": "select",
            "options": ["Phone", "Email", "Post"],
            "required": True
        },
        {
            "id": "question_6",
            "question_text": "I am making this complaint anonymously",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "section_2",
            "question_text": "Representative Information",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_7",
            "question_text": "Your Name (if making the complaint on behalf of another person)",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "question_8",
            "question_text": "What is your relationship to the person?",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "question_9",
            "question_text": "Does the person know you are making this complaint/providing feedback?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": False
        },
        {
            "id": "question_10",
            "question_text": "Does the person consent to the complaint/feedback being made?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": False
        },
        {
            "id": "question_11",
            "question_text": "Preferred contact method",
            "field_type": "select",
            "options": ["Phone", "Email", "Post"],
            "required": False
        },
        {
            "id": "section_3",
            "question_text": "Complaint Details",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_12",
            "question_text": "Name of the person, or the service about whom you are complaining",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_13",
            "question_text": "Contact Details (if known)",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "question_14",
            "question_text": "What is your Complaint/Feedback about? Provide some details to help us understand your concerns. You should include what happened, where it happened, time it happened and who was involved.",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_15",
            "question_text": "Supporting Information: Please attach copies of any documentation that may help us to investigate your complaint/feedback (for example letters, references, emails).",
            "field_type": "textarea",
            "options": [],
            "required": False
        },
        {
            "id": "question_16",
            "question_text": "What outcomes are you seeking because of the complaint/feedback?",
            "field_type": "textarea",
            "options": [],
            "required": True
        }
    ]

def is_complaints_form(file_path: str) -> bool:
    """
    Determine if the file is likely a Complaints Form.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be a complaints form
    """
    # Check the filename for a quick identification
    import os
    filename = os.path.basename(file_path).lower()
    
    if "complaint" in filename or "complaints form" in filename or "feedback form" in filename:
        return True
    
    # If filename doesn't contain clear indicators, try to detect from content
    if file_path.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        try:
            # Try to extract some text from the file
            from services.document.document_service import extract_text_from_file
            text_content = extract_text_from_file(file_path)
            
            # Check for key phrases that would indicate this is a complaints form
            if text_content:
                indicators = [
                    "making this complaint",
                    "what is your complaint",
                    "providing feedback",
                    "complaint anonymously"
                ]
                
                text_lower = text_content.lower()
                return any(indicator in text_lower for indicator in indicators)
            
        except Exception as e:
            print(f"Error checking complaints form content: {e}")
            
    return False