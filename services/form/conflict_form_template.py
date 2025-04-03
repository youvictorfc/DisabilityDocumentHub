"""
Template-based fallback solution for the Conflict of Interest Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any

def get_conflict_form_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Conflict of Interest Form 
    with the exact structure matching the document.
    """
    return [
        {
            "id": "section_1",
            "question_text": "SECTION 1: PERSONAL DETAILS",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_1",
            "question_text": "Name:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_2",
            "question_text": "Job Title / Area of Responsibility:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_3",
            "question_text": "Phone:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_4",
            "question_text": "Email:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "section_2",
            "question_text": "SECTION 2: DISCLOSURE DETAILS",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_5",
            "question_text": "The actual, potential, or perceived conflict of interest relates to: (tick all appropriate box/s)",
            "field_type": "checkbox",
            "options": [
                "Management",
                "Staff recruitment",
                "Outside work activities (paid/unpaid)",
                "Relationship with external parties",
                "Financial interest",
                "Gifts/benefits",
                "Provision of external consultancy services",
                "Participant",
                "Other (if you selected other, please provide details)",
                "Participant enrolled in another provider"
            ],
            "required": True
        },
        {
            "id": "question_6",
            "question_text": "The following actual, potential, or perceived conflict of interest has been identified. (Please insert all relevant details)",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_7",
            "question_text": "The (actual, potential, or perceived) conflict is expected to last:(tick appropriate box)",
            "field_type": "radio",
            "options": [
                "0–12 months",
                ">12 months or ongoing"
            ],
            "required": True
        },
        {
            "id": "section_3",
            "question_text": "SECTION 3: TO BE COMPLETED BY THE PRINCIPAL / PROVIDER",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_8",
            "question_text": "In my opinion the details provided: (tick appropriate box)",
            "field_type": "radio",
            "options": [
                "Do not constitute a conflict of interest, and I authorise the employee to continue the activity (go to Section 4).",
                "Do constitute an actual, potential, or perceived conflict of interest (please provide a detailed action plan below)."
            ],
            "required": True
        },
        {
            "id": "question_9",
            "question_text": "I have reviewed the above considerations and request that the Employee takes the following action to eliminate/manage the conflict:",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_10",
            "question_text": "I will ensure this action plan is reviewed:",
            "field_type": "radio",
            "options": [
                "Within 1 month",
                "Within 3 months",
                "Within 6 months",
                "Within 12 months",
                "Other – specify",
                "N/A: the conflict is one-off or short duration"
            ],
            "required": True
        },
        {
            "id": "section_4",
            "question_text": "SECTION 4: DECLARATION",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_11",
            "question_text": "To the best of my knowledge and belief any actual, perceived, or potential conflicts between my duties as a stakeholder of Minto Disability Services and my private and/or business interests have been fully disclosed in this form in accordance with the requirements of Minto Disability Services Conflict of Interest Policy. I acknowledge, and agree to comply with, any approach identified in this form for removing or managing an actual, perceived, or potential conflict of interest.",
            "field_type": "readonly",
            "options": [],
            "required": False
        },
        {
            "id": "question_12",
            "question_text": "Signature:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_13",
            "question_text": "Date:",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "section_5",
            "question_text": "SECTION 5: PRINCIPAL / PROVIDER",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_14",
            "question_text": "The actions described in the approach outlined in Section 3 have been put in place to effectively manage any actual, potential, or perceived conflict of interest disclosed in Section 2. The approach outlined in Section 3 ensures that the Minto Disability Services public interests and reputation is adequately protected.",
            "field_type": "readonly",
            "options": [],
            "required": False
        },
        {
            "id": "question_15",
            "question_text": "Name:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_16",
            "question_text": "Signature:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_17",
            "question_text": "Date:",
            "field_type": "date",
            "options": [],
            "required": True
        }
    ]

def is_conflict_form(file_path: str) -> bool:
    """
    Determine if the file is likely a Conflict of Interest form.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be a conflict of interest form
    """
    # Check the filename for a quick identification
    import os
    filename = os.path.basename(file_path).lower()
    
    if "conflict" in filename or "conflict of interest" in filename or "coi" in filename:
        return True
    
    # If filename doesn't contain clear indicators, try to detect from content
    if file_path.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
        try:
            # Try to extract some text from the file
            from services.document.document_service import extract_text_from_file
            text_content = extract_text_from_file(file_path)
            
            # Check for key phrases that would indicate this is a conflict of interest form
            if text_content:
                indicators = [
                    "conflict of interest",
                    "disclosure details",
                    "perceived conflict",
                    "actual, potential, or perceived conflict"
                ]
                
                text_lower = text_content.lower()
                return any(indicator in text_lower for indicator in indicators)
            
        except Exception as e:
            print(f"Error checking conflict form content: {e}")
            
    return False