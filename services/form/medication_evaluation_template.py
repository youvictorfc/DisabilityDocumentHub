"""
Template-based fallback solution for the Administration of Medication Evaluation Checklist
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import re
import os

def get_medication_evaluation_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Administration of Medication Evaluation Checklist
    with the exact structure matching the document.
    """
    template = []
    
    # Observer and staff member information
    template.append({
        "id": "observer_name",
        "question_text": "I ………………………………………………………… have observed ……………………………………………………",
        "field_type": "text",
        "required": True
    })
    
    # Medication categories
    template.append({
        "id": "medication_categories",
        "question_text": "administer medication in the following medication categories: Oral, Topical, Eye/Ear Drops.",
        "field_type": "checkbox",
        "options": ["Oral", "Topical", "Eye", "Ear Drops"],
        "required": True
    })
    
    # Assessment outcomes
    template.append({
        "id": "satisfied_with_administration",
        "question_text": "I am satisfied that the staff member can administer medication according to policy and procedure",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": True
    })
    
    template.append({
        "id": "requires_assistance",
        "question_text": "I consider that the staff member requires further assistance / coaching",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    # Nose administration
    template.append({
        "id": "nose_administration",
        "question_text": "Nose: sprays or drops",
        "field_type": "checkbox",
        "options": ["Sprays", "Drops"],
        "required": True
    })
    
    # Ears administration
    template.append({
        "id": "ears_administration",
        "question_text": "Ears: drops",
        "field_type": "checkbox",
        "options": ["Drops"],
        "required": True
    })
    
    # Skin administration
    template.append({
        "id": "skin_administration",
        "question_text": "Skin: application of ointments in lotion, cream or liquid, sprays and transdermal adhesive patches.",
        "field_type": "checkbox",
        "options": ["Ointments in lotion", "Cream", "Liquid", "Sprays", "Transdermal adhesive patches"],
        "required": True
    })
    
    # Signature fields
    template.append({
        "id": "supervisor_details",
        "question_text": "To be completed and signed by the staff member and the workplace manager / supervisor or a workplace assessor who has observed the task.",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "note_further_coaching",
        "question_text": "note: Should the staff member require further coaching this is to be scheduled as soon as possible and a time made for another opportunity to complete the checklist.",
        "field_type": "text",
        "required": False
    })
    
    # Add the checklist sections - PREPARE TO ASSIST WITH MEDICATION
    prepare_questions = [
        "Staff is aware of medication/schedule of support plan",
        "Staff reminds person it is time to take medication",
        "Locates and reads treatment sheet / medication chart / care / health plan relevant to the client",
        "Identifies the level of physical assistance required by the person",
        "Identifies the level of support required for the person to self-administer",
        "Identifies the person's current physical and behavioural condition",
        "Collects medication from locked storage area",
        "Collects all equipment required: e.g., medication cup /glass, tissues, applicators, swabs",
        "Checks the treatment sheet for correct medication, time, and date",
        "Checks medication container: Dossett/Webster Pak or original container to ensure medication corresponds with treatment sheet / care / health plan",
        "Reads and follow any special instructions for administration of the medication",
        "Checks treatment sheet / manufacturer's instructions for correct application procedure relevant to medication type",
        "Demonstrates that person confidentiality, privacy and dignity is maintained",
        "Completes personal hygiene procedures as per infection control guidelines"
    ]
    
    template.append({
        "id": "prepare_checklist",
        "question_text": "PREPARE TO ASSIST WITH MEDICATION",
        "field_type": "checklist_table",
        "options": prepare_questions,
        "columns": ["Yes", "No"], 
        "required": True
    })
    
    # PREPARE THE PERSON FOR ASSISTANCE WITH MEDICATION
    prepare_person_questions = [
        "Identifies correct person and explains the administration procedure to person",
        "Demonstrates appropriate communication to engage person in the activity",
        "Provides opportunity for person to actively participate in the procedure",
        "Checks medication in relation to person information",
        "Observes person to check for physical or behavioural changes and identifies the reporting process if there are differences",
        "Identifies and describes circumstances in which the appropriate action is to report observed health status rather than proceed with the administration and seek advice from health professional",
        "Checks documentation and instructions and person prepared"
    ]
    
    template.append({
        "id": "prepare_person_checklist",
        "question_text": "PREPARE THE PERSON FOR ASSISTANCE WITH MEDICATION",
        "field_type": "checklist_table",
        "options": prepare_person_questions,
        "columns": ["Yes", "No"],
        "required": True
    })
    
    # ASSIST PERSON WITH MEDICATION
    assist_questions = [
        "Follows correct procedure for specific medication type",
        "Uses appropriate equipment for specific medication type",
        "Follows correct application/administration procedure according to treatment sheet/care/health plan",
        "Provides correct level of assistance according to person information",
        "Informs person of process throughout the administration",
        "Provides privacy according to person preference and context",
        "Disposes of equipment safely and correctly"
    ]
    
    template.append({
        "id": "assist_checklist",
        "question_text": "ASSIST PERSON WITH MEDICATION",
        "field_type": "checklist_table",
        "options": assist_questions,
        "columns": ["Yes", "No"],
        "required": True
    })
    
    # SUPPORT THE PERSON TO COMPLETE THE MEDICATION PROCESS
    support_questions = [
        "Observes to ensure medication has been taken",
        "Provides person with correct resources to assist with medication",
        "Responds to person's queries, concerns, and adverse reaction/s appropriately",
        "Completes the process according to medication procedure",
        "Documents medication administration has occurred according to organisation requirements"
    ]
    
    template.append({
        "id": "support_checklist",
        "question_text": "SUPPORT THE PERSON TO COMPLETE THE MEDICATION PROCESS", 
        "field_type": "checklist_table",
        "options": support_questions,
        "columns": ["Yes", "No"],
        "required": True
    })
    
    # CLEAN UP
    clean_questions = [
        "Returns and stores materials and equipment according to manufacturer's instructions",
        "Cleans used equipment as required",
        "Secures medication according to organisation policy and procedures",
        "Completes activities in accordance with infection control procedures"
    ]
    
    template.append({
        "id": "clean_checklist",
        "question_text": "CLEAN UP",
        "field_type": "checklist_table",
        "options": clean_questions,
        "columns": ["Yes", "No"],
        "required": True
    })
    
    # RECORDS
    records_questions = [
        "Records outcome of procedure accurately on treatment sheet",
        "Records observations of person's physical, emotional, behavioural changes",
        "Records/documents time, date, details of medication administered, and signature",
        "Records/documents special instructions/conditions"
    ]
    
    template.append({
        "id": "records_checklist",
        "question_text": "RECORDS", 
        "field_type": "checklist_table",
        "options": records_questions,
        "columns": ["Yes", "No"],
        "required": True
    })
    
    # PROVIDE FEEDBACK
    feedback_questions = [
        "Clarifies any concerns with appropriate personnel",
        "Provides person with feedback that supports positive self-image, feelings of security and confidence",
        "Reports observation to relevant personnel",
        "Recognises and reports changes in person that may have Medication implications",
        "Provides feedback to relevant personnel regarding person's needs, concerns, safety and wellbeing"
    ]
    
    template.append({
        "id": "feedback_checklist",
        "question_text": "PROVIDE FEEDBACK",
        "field_type": "checklist_table",
        "options": feedback_questions,
        "columns": ["Yes", "No"],
        "required": True
    })
    
    return template


def is_medication_evaluation_checklist(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a Medication Evaluation Checklist form.
    
    Args:
        file_path_or_content: The path to the file or the content as a string
        
    Returns:
        bool: True if the file appears to be a medication evaluation checklist
    """
    try:
        content = ""
        
        # Check if the input is a file path
        if os.path.exists(file_path_or_content):
            # Assume it's a text file or already content
            with open(file_path_or_content, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        else:
            # Assume it's already content
            content = file_path_or_content
            
        # Define keywords and patterns that indicate this is a medication evaluation checklist
        keywords = [
            r"administration\s+of\s+medication\s+evaluation\s+checklist",
            r"administer\s+medication",
            r"medication\s+categories",
            r"oral",
            r"topical",
            r"eye/ear\s+drops",
            r"AMEC",
            r"prepare\s+to\s+assist\s+with\s+medication"
        ]
        
        # Create a scoring system - if enough keywords are found, consider it a match
        score = 0
        for keyword in keywords:
            if re.search(keyword, content.lower()):
                score += 1
                
        # If 3 or more keywords match, consider it a medication evaluation checklist
        return score >= 3
        
    except Exception:
        # If there's any error in processing, default to False
        return False