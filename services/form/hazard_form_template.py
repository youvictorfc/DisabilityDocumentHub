"""
Template-based fallback solution for the Hazard Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any

def get_hazard_form_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Hazard Form 
    with the exact structure matching the document.
    """
    return [
        {
            "id": "section_1",
            "question_text": "Information",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_1",
            "question_text": "Person's Name",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_2",
            "question_text": "Date",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "question_3",
            "question_text": "Category",
            "field_type": "radio",
            "options": ["Employee", "Client", "Visitor", "Other"],
            "required": True
        },
        {
            "id": "question_4",
            "question_text": "Address",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "question_5",
            "question_text": "Home Phone",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "question_6",
            "question_text": "Mobile Phone",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "section_2",
            "question_text": "Hazard Details",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_7",
            "question_text": "Date of Hazard Identification",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "question_8",
            "question_text": "Time of Hazard Identification",
            "field_type": "time",
            "options": [],
            "required": True
        },
        {
            "id": "question_9",
            "question_text": "Location of hazard",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_10",
            "question_text": "Who was the hazard reported to?",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_11",
            "question_text": "Position",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_12",
            "question_text": "Date Reported",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "question_13",
            "question_text": "Was anyone injured because of the hazard?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True,
            "help_text": "If yes, an Injury Report must also be completed."
        },
        {
            "id": "question_14",
            "question_text": "What caused this report to be recorded? Describe what happened and what you did about it. (Include area and task involved and any equipment, tools or people involved. Attach additional pages if required)",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_15",
            "question_text": "What short term action/s have been taken? (Attach additional pages if required)",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_16",
            "question_text": "Include any suggestions for reducing or eliminating the problem? (e.g., use of mechanical devices or training). (Attach additional pages if required)",
            "field_type": "textarea",
            "options": [],
            "required": False
        },
        {
            "id": "section_3",
            "question_text": "Manager to Complete",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_17",
            "question_text": "Hazard Category",
            "field_type": "checkboxes",
            "options": ["Physical", "Chemical", "Biological", "Psychological", "Ergonomic", "Other"],
            "required": True
        },
        {
            "id": "question_18",
            "question_text": "Date",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "question_19",
            "question_text": "Upon investigation of the above hazard, please provide any information, further actions, who will follow this up and when this will occur: (attach additional pages if required)",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_20",
            "question_text": "Please provide details about the outcome evaluation:",
            "field_type": "checkboxes",
            "options": ["Hazard Eliminated", "Risk Controlled"],
            "required": True,
            "help_text": "(Attach any relevant evidence e.g., invoices of work completed, records of action taken)"
        },
        {
            "id": "question_21",
            "question_text": "HAZPAK RISK SCORE",
            "field_type": "text",
            "options": [],
            "required": True,
            "help_text": "As per the Risk Matrix, Senior Manager must be notified immediately for risk scores of 1 or 2"
        },
        {
            "id": "question_22",
            "question_text": "Manager Name",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_23",
            "question_text": "Senior Manager (If risk score 1 or 2)",
            "field_type": "text",
            "options": [],
            "required": False
        },
        {
            "id": "section_4",
            "question_text": "Form Submission Instructions",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_24",
            "question_text": "This form is to be forwarded to the relevant Service Manager/Coordinator (file in Risk Management folder), with a copy to Human Resources",
            "field_type": "readonly",
            "options": [],
            "required": False
        }
    ]

def is_hazard_form(file_path: str) -> bool:
    """
    Determine if the file is likely a Hazard Form.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be a hazard form
    """
    # Check the filename for a quick identification
    import os
    filename = os.path.basename(file_path).lower()
    
    if "hazard" in filename or "hazard form" in filename:
        return True
    
    # If filename doesn't contain clear indicators, try to detect from content
    if file_path.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        try:
            # Try to extract some text from the file
            from services.document.document_service import extract_text_from_file
            text_content = extract_text_from_file(file_path)
            
            # Check for key phrases that would indicate this is a hazard form
            if text_content:
                indicators = [
                    "hazard details",
                    "date of hazard identification",
                    "location of hazard",
                    "hazpak risk score",
                    "hazard category"
                ]
                
                text_lower = text_content.lower()
                return any(indicator in text_lower for indicator in indicators)
            
        except Exception as e:
            print(f"Error checking hazard form content: {e}")
            
    return False