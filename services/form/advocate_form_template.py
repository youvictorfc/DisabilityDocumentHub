"""
Template-based fallback solution for the Act as an Advocate Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any

def get_advocate_form_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Act as an Advocate Form 
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
            "question_text": "Name",
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
            "id": "section_2",
            "question_text": "Advocacy Information",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_5",
            "question_text": "Name of the person you are advocating for",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_6",
            "question_text": "Your relationship to this person",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_7",
            "question_text": "Does this person know you are advocating on their behalf?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "question_8",
            "question_text": "If no, please explain why",
            "field_type": "textarea",
            "options": [],
            "required": False,
            "conditional": {
                "dependent_on": "question_7",
                "show_if": "No"
            }
        },
        {
            "id": "section_3",
            "question_text": "Issue Information",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_9",
            "question_text": "Please describe the issue you are advocating about",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_10",
            "question_text": "What outcome are you seeking?",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_11",
            "question_text": "Have you attempted to resolve this issue directly?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "question_12",
            "question_text": "If yes, please describe what steps you have taken",
            "field_type": "textarea",
            "options": [],
            "required": False,
            "conditional": {
                "dependent_on": "question_11",
                "show_if": "Yes"
            }
        },
        {
            "id": "section_4",
            "question_text": "Supporting Documentation",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_13",
            "question_text": "Do you have any supporting documentation for this issue?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "question_14",
            "question_text": "If yes, please list the documents you have",
            "field_type": "textarea",
            "options": [],
            "required": False,
            "conditional": {
                "dependent_on": "question_13",
                "show_if": "Yes"
            }
        },
        {
            "id": "section_5",
            "question_text": "Consent",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_15",
            "question_text": "I consent to Minto Disability Services storing and using this information for advocacy purposes",
            "field_type": "checkbox",
            "options": ["I consent"],
            "required": True
        },
        {
            "id": "question_16",
            "question_text": "I understand that I can withdraw this consent at any time",
            "field_type": "checkbox",
            "options": ["I understand"],
            "required": True
        },
        {
            "id": "question_17",
            "question_text": "Signature",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_18",
            "question_text": "Date",
            "field_type": "date",
            "options": [],
            "required": True
        }
    ]

def is_advocate_form(file_path: str) -> bool:
    """
    Determine if the file is likely an Act as an Advocate form.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be an advocate form
    """
    # Check the filename for a quick identification
    import os
    filename = os.path.basename(file_path).lower()
    
    if "act as an advocate" in filename or "advocate form" in filename:
        return True
    
    # If filename doesn't contain clear indicators, try to detect from content
    if file_path.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        try:
            # Try to extract some text from the file
            from services.document.document_service import extract_text_from_file
            text_content = extract_text_from_file(file_path)
            
            # Check for key phrases that would indicate this is an advocate form
            if text_content:
                indicators = [
                    "act as an advocate",
                    "advocacy form",
                    "advocating for",
                    "advocate on behalf"
                ]
                
                text_lower = text_content.lower()
                return any(indicator in text_lower for indicator in indicators)
            
        except Exception as e:
            print(f"Error checking advocate form content: {e}")
            
    return False