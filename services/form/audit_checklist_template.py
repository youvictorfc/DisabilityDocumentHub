"""
Template-based fallback solution for the Access Audit Checklist form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any

def get_access_audit_checklist_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Access Audit Checklist form
    with the exact structure matching the document.
    """
    return [
        {
            "id": "section_1",
            "question_text": "Building/Site Information",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_1",
            "question_text": "Building Name",
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
            "question_text": "Date of Assessment",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "question_4",
            "question_text": "Assessor Name",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "section_2",
            "question_text": "Exterior Access",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_5",
            "question_text": "Is there accessible parking available?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_6",
            "question_text": "Is the accessible parking clearly marked?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_7",
            "question_text": "Is there a clear accessible path from parking to entrance?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_8",
            "question_text": "Are exterior paths at least 1000mm wide?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_9",
            "question_text": "Are paths free from obstacles?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_10",
            "question_text": "Are paths firm, stable, and slip-resistant?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "section_3",
            "question_text": "Entrances",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_11",
            "question_text": "Is the main entrance accessible?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_12",
            "question_text": "If not, is there an alternative accessible entrance?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": False
        },
        {
            "id": "question_13",
            "question_text": "Is the doorway at least 850mm wide?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_14",
            "question_text": "Can the entrance door be operated with minimal force?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_15",
            "question_text": "Are door handles within accessible reach range (900-1100mm)?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "section_4",
            "question_text": "Interior Circulation",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_16",
            "question_text": "Are corridors at least 1000mm wide?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_17",
            "question_text": "Are floor surfaces stable, firm, and slip-resistant?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_18",
            "question_text": "Are interior doors easy to open?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_19",
            "question_text": "Do door handles allow for easy gripping?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "section_5",
            "question_text": "Vertical Circulation",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_20",
            "question_text": "If multi-level, is there an accessible elevator?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": False
        },
        {
            "id": "question_21",
            "question_text": "Are stairs equipped with handrails on both sides?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": False
        },
        {
            "id": "question_22",
            "question_text": "Are stair nosings clearly visible?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": False
        },
        {
            "id": "question_23",
            "question_text": "Are ramps provided where needed?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": False
        },
        {
            "id": "question_24",
            "question_text": "Do ramps have appropriate slope (1:14 or less)?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": False
        },
        {
            "id": "section_6",
            "question_text": "Restrooms",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_25",
            "question_text": "Is there at least one accessible toilet?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_26",
            "question_text": "Is the accessible toilet clearly signed?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_27",
            "question_text": "Is there adequate turning space (1500mm diameter)?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_28",
            "question_text": "Are grab bars installed?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_29",
            "question_text": "Is the sink accessible with knee clearance?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "section_7",
            "question_text": "Signage and Wayfinding",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_30",
            "question_text": "Is signage clear and consistent throughout?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_31",
            "question_text": "Is text large enough and high contrast?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_32",
            "question_text": "Are accessible features clearly identified?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "section_8",
            "question_text": "Emergency Systems",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_33",
            "question_text": "Are visual alarms provided?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_34",
            "question_text": "Are evacuation procedures accessible to all?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "question_35",
            "question_text": "Are emergency exits accessible?",
            "field_type": "radio",
            "options": ["Yes", "No", "N/A"],
            "required": True
        },
        {
            "id": "section_9",
            "question_text": "Additional Notes and Recommendations",
            "field_type": "heading",
            "options": [],
            "required": False
        },
        {
            "id": "question_36",
            "question_text": "Major accessibility issues identified:",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_37",
            "question_text": "Recommended improvements:",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "question_38",
            "question_text": "Estimated timeline for corrections:",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "question_39",
            "question_text": "Follow-up assessment date:",
            "field_type": "date",
            "options": [],
            "required": True
        }
    ]


def is_access_audit_checklist(file_path: str) -> bool:
    """
    Determine if the file is likely an access audit checklist.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be an access audit checklist
    """
    filename = file_path.lower()
    return ('access' in filename and 'audit' in filename) or \
           ('access' in filename and 'checklist' in filename) or \
           ('accessibility' in filename and 'audit' in filename)