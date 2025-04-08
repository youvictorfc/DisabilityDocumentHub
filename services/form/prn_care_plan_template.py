"""
PRN Care Plan Template
Specialized template for the PRN Care Plan form, ensuring proper extraction of all fields.
"""

from flask import current_app
import logging
import re

def is_prn_care_plan_form(file_path, content=None):
    """
    Check if the provided file is a PRN Care Plan form based on its name
    or content (looking for key terms).
    
    Args:
        file_path: Path to the file
        content: Optional content of the file for content-based matching
        
    Returns:
        bool: Whether this is a PRN Care Plan form
    """
    # Check filename
    filename_match = False
    if file_path:
        file_name = file_path.lower()
        if 'prn care plan' in file_name or 'prn_care_plan' in file_name:
            filename_match = True
    
    # If we have content and haven't matched by filename, check content
    content_match = False
    if content and not filename_match:
        # Look for key phrases that would indicate this is a PRN Care Plan
        key_phrases = [
            "prn medication",
            "prn staff information",
            "medication name",
            "prescribed by",
            "review process",
            "restrictive practice approval"
        ]
        
        # Calculate a match score based on how many key phrases are found
        match_score = sum(1 for phrase in key_phrases if phrase.lower() in content.lower())
        content_match = match_score >= 3  # If at least 3 key phrases are found
    
    return filename_match or content_match

def extract_prn_care_plan_fields(content):
    """
    Extract fields from a PRN Care Plan form.
    
    Args:
        content: Text content of the form
        
    Returns:
        dict: Structured representation of the form with questions array
    """
    current_app.logger.info("Extracting fields using PRN Care Plan template")
    
    # Define the fields we expect in this form
    form_questions = [
        # Personal Details section
        {
            "id": "personal_details_header",
            "question_text": "Personal Details",
            "field_type": "header",
            "options": [],
            "required": False
        },
        {
            "id": "name",
            "question_text": "Name",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "date_of_birth",
            "question_text": "Date of Birth",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "restrictive_practice_approval",
            "question_text": "Restrictive Practice Approval",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True
        },
        {
            "id": "review_date",
            "question_text": "Review date",
            "field_type": "date",
            "options": [],
            "required": True
        },
        
        # PRN Medication section
        {
            "id": "prn_medication_header",
            "question_text": "PRN Medication",
            "field_type": "header",
            "options": [],
            "required": False
        },
        {
            "id": "medication_name",
            "question_text": "Medication Name",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "prescribed_by",
            "question_text": "Prescribed by",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "medication_label_info",
            "question_text": "Information from medication label",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "route",
            "question_text": "Route e.g., oral",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "time",
            "question_text": "Time",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "dose",
            "question_text": "Dose",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "dosage_strength",
            "question_text": "Dosage strength",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "frequency",
            "question_text": "Frequency",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "interval_doses",
            "question_text": "Interval between doses",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "max_doses_24hr",
            "question_text": "Maximum number of doses in 24 hr period",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "directions",
            "question_text": "Directions e.g., relationship to other medication",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        
        # PRN Staff Information section
        {
            "id": "prn_staff_info_header",
            "question_text": "PRN Staff Information",
            "field_type": "header",
            "options": [],
            "required": False
        },
        {
            "id": "medication_start_date",
            "question_text": "Date when medication was started by prescriber",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "reason_for_use",
            "question_text": "Reason for use of the medication",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "expected_outcome",
            "question_text": "Expected outcome of the medication",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "trained_staff",
            "question_text": "Identify staff trained in use of PRN and any potential reactions",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "person_observing_need",
            "question_text": "Person responsible for observing need for medication",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "person_initiating_admin",
            "question_text": "Person responsible for initiating the administration of medication",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "alternatives",
            "question_text": "Alternatives / other course of action prior to use of PRN",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "decision_maker",
            "question_text": "Decision maker to offer medication",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "person_determining_dosage",
            "question_text": "Person responsible to determine dosage if dosage states 1 or 2 tablets",
            "field_type": "text",
            "options": [],
            "required": True
        },
        
        # Description section
        {
            "id": "description_header",
            "question_text": "Description (as much detail below as possible using the following as prompts",
            "field_type": "header",
            "options": [],
            "required": False
        },
        {
            "id": "behaviours",
            "question_text": "Behaviours",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "triggers",
            "question_text": "Triggers",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "communication_methods",
            "question_text": "Methods of communication",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "symptoms",
            "question_text": "Symptoms to look out for possible alternatives to attempt before giving medication",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "when_to_refer",
            "question_text": "When to refer to prescriber",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "indicators",
            "question_text": "Indicators",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "when_to_offer_medication",
            "question_text": "How you will know when to offer the medication where to record the outcome",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        
        # Review Process section
        {
            "id": "review_process_header",
            "question_text": "Review Process",
            "field_type": "header",
            "options": [],
            "required": False
        },
        {
            "id": "review_date_final",
            "question_text": "Review date",
            "field_type": "date",
            "options": [],
            "required": True
        },
        {
            "id": "meeting_outcomes",
            "question_text": "Is the medication meeting outcome/s listed?",
            "field_type": "textarea",
            "options": [],
            "required": True
        },
        {
            "id": "review_date_recorded",
            "question_text": "Review date recorded in plans and linked to calendar for action",
            "field_type": "checkbox",
            "options": ["Support Plan", "Linked to calendar"],
            "required": True
        },
        {
            "id": "person_undertaking_review",
            "question_text": "Person responsible for undertaking review",
            "field_type": "text",
            "options": [],
            "required": True
        },
        {
            "id": "signature",
            "question_text": "Signature",
            "field_type": "signature",
            "options": [],
            "required": True
        }
    ]
    
    return {"questions": form_questions}