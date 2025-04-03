"""
Template-based fallback solution for the Hazardous Substances Checklist
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any


def get_hazardous_substances_checklist_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Hazardous Substances Checklist
    with the exact structure matching the document.
    """
    return [
        {
            "id": "introduction",
            "question_text": "Hazardous substances in the household may include chemicals such as methylated spirits, caustic soda, oven cleaners, general cleaning agents, pesticides, disinfectants, medicine (i.e., cytotoxic drugs) and others. Tick the appropriate response. A \"No\" answer means that the hazards should be assessed, and control measures considered where the assessment indicates it is necessary.",
            "field_type": "information",
            "required": False
        },
        {
            "id": "frequency",
            "question_text": "Frequency of the assessment",
            "field_type": "text",
            "required": True
        },
        {
            "id": "date",
            "question_text": "Date of inspection",
            "field_type": "date",
            "required": True
        },
        {
            "id": "address",
            "question_text": "Address of the site",
            "field_type": "text",
            "required": True
        },
        {
            "id": "emergency_procedures",
            "question_text": "Is the worker aware of emergency procedures in case of an accident involving the substance?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "emergency_procedures_comments",
            "question_text": "Comments/hazard report completed for emergency procedures",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "containers_labelled",
            "question_text": "Are containers clearly labelled?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "containers_labelled_comments",
            "question_text": "Comments/hazard report completed for container labelling",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "original_containers",
            "question_text": "Are substances in original containers?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "original_containers_comments",
            "question_text": "Comments/hazard report completed for original containers",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "stored_appropriately",
            "question_text": "Are substances stored appropriately (out of reach of children?)",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "stored_appropriately_comments",
            "question_text": "Comments/hazard report completed for storage",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "trained_in_procedures",
            "question_text": "Have workers been trained in safe procedures when working with the substance including personal protective equipment?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "trained_in_procedures_comments",
            "question_text": "Comments/hazard report completed for training",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "health_effects",
            "question_text": "Does the worker experience any health effects from contact with the substance?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "health_effects_comments",
            "question_text": "Comments/hazard report completed for health effects",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "protective_equipment",
            "question_text": "Does the worker have personal protective equipment for work with the substance?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "protective_equipment_comments",
            "question_text": "Comments/hazard report completed for protective equipment",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "ventilation",
            "question_text": "Is there an exhaust fan or open window for adequate ventilation, when using the substance?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "ventilation_comments",
            "question_text": "Comments/hazard report completed for ventilation",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "substitution",
            "question_text": "Can the use of the substance be eliminated or substituted for a less hazardous substance?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "substitution_comments",
            "question_text": "Comments/hazard report completed for substance substitution",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "sds_register",
            "question_text": "Is the SDS (safety data sheet) register for all substances identified and accessible to workers?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "sds_register_comments",
            "question_text": "Comments/hazard report completed for SDS register",
            "field_type": "textarea",
            "required": False
        },
        {
            "id": "risk_assessment",
            "question_text": "Has the risk assessment been done and recorded for all hazardous substances?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "risk_assessment_comments",
            "question_text": "Comments/hazard report completed for risk assessment",
            "field_type": "textarea",
            "required": False
        }
    ]


def is_hazardous_substances_checklist(file_path: str) -> bool:
    """
    Determine if the file is likely a Hazardous Substances Checklist.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be a hazardous substances checklist
    """
    from services.document.document_service import extract_text_from_file
    
    try:
        # Extract text from file
        content = extract_text_from_file(file_path)
        
        # If content couldn't be extracted, return False
        if not content:
            return False
        
        # Check for key phrases/indicators from the hazardous substances checklist
        indicators = [
            "hazardous substances in the household",
            "containers clearly labelled",
            "substances in original containers",
            "safety data sheet",
            "SDS register"
        ]
        
        # Check for at least 3 of the indicators
        matches = sum(1 for indicator in indicators if indicator.lower() in content.lower())
        
        # If the filename contains a clear indication, or we have multiple content matches, it's likely a match
        if "hazardous substances checklist" in file_path.lower() or matches >= 3:
            return True
            
        return False
        
    except Exception as e:
        # Log the error but don't raise it
        print(f"Error checking if file is a hazardous substances checklist: {str(e)}")
        return False